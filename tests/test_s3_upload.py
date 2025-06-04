import json
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Import the app module directly using the file path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from s3_upload import app

@pytest.fixture
def mock_s3_client():
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3

def test_generate_signed_url_success(mock_s3_client):
    # Mock successful URL generation
    mock_s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/test-key?signature=abc"
    
    # Call the function
    result = app.generate_signed_url("test.jpg", "image/jpeg")
    
    # Verify the result
    assert result["signed_url"] == "https://test-bucket.s3.amazonaws.com/test-key?signature=abc"
    assert "file_key" in result
    assert result["bucket"] == app.BUCKET_NAME
    assert result["expiration_seconds"] == app.EXPIRATION
    assert result["max_size"] == app.MAX_UPLOAD_SIZE
    
    # Verify the S3 client was called correctly
    mock_s3_client.generate_presigned_url.assert_called_once()
    call_args = mock_s3_client.generate_presigned_url.call_args[0]
    call_kwargs = mock_s3_client.generate_presigned_url.call_args[1]
    assert call_args[0] == 'put_object'
    assert call_kwargs['Params']['Bucket'] == app.BUCKET_NAME
    assert call_kwargs['Params']['ContentType'] == "image/jpeg"
    assert call_kwargs['ExpiresIn'] == app.EXPIRATION

def test_generate_signed_url_s3_error(mock_s3_client):
    # Mock S3 client error
    error_response = {
        'Error': {
            'Code': 'AccessDenied',
            'Message': 'Access Denied'
        }
    }
    mock_s3_client.generate_presigned_url.side_effect = ClientError(
        error_response=error_response,
        operation_name='PutObject'
    )
    
    # Test with S3 error
    with pytest.raises(Exception) as excinfo:
        app.generate_signed_url("test.jpg", "image/jpeg")
    
    assert "Failed to generate signed URL" in str(excinfo.value)
    assert "Access Denied" in str(excinfo.value)

def test_lambda_handler_success(mock_s3_client):
    # Mock successful URL generation
    mock_s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/test-key?signature=abc"
    
    # Create test event
    event = {
        "body": json.dumps({
            "file_name": "test.jpg",
            "content_type": "image/jpeg"
        })
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Verify the response
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["signed_url"] == "https://test-bucket.s3.amazonaws.com/test-key?signature=abc"
    assert "file_key" in body

def test_lambda_handler_missing_file_name():
    # Create test event with missing file_name
    event = {
        "body": json.dumps({
            "content_type": "image/jpeg"
        })
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Verify the response
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
    assert "Missing required parameter" in body["error"]

def test_lambda_handler_s3_error(mock_s3_client):
    # Mock S3 client error
    error_response = {
        'Error': {
            'Code': 'AccessDenied',
            'Message': 'Access Denied'
        }
    }
    mock_s3_client.generate_presigned_url.side_effect = ClientError(
        error_response=error_response,
        operation_name='PutObject'
    )
    
    # Create test event
    event = {
        "body": json.dumps({
            "file_name": "test.jpg",
            "content_type": "image/jpeg"
        })
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Verify the response
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
    assert "Internal server error" in body["error"]