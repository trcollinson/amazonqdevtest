import json
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Import the app module directly using the file path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from website_to_text import app

@pytest.fixture
def mock_trafilatura():
    with patch('trafilatura.fetch_url') as mock_fetch:
        with patch('trafilatura.extract') as mock_extract:
            yield mock_fetch, mock_extract

@pytest.fixture
def mock_bedrock_client():
    with patch('boto3.client') as mock_client:
        mock_bedrock = MagicMock()
        mock_client.return_value = mock_bedrock
        yield mock_bedrock

def test_extract_content_success(mock_trafilatura):
    mock_fetch, mock_extract = mock_trafilatura
    
    # Mock successful content extraction
    mock_fetch.return_value = "<html><body><h1>Test Content</h1><p>This is a test.</p></body></html>"
    mock_extract.return_value = "# Test Content\n\nThis is a test."
    
    # Call the function
    result = app.extract_content("https://example.com")
    
    # Verify the result
    assert result == "# Test Content\n\nThis is a test."
    mock_fetch.assert_called_once_with("https://example.com")
    mock_extract.assert_called_once()

def test_extract_content_invalid_url(mock_trafilatura):
    mock_fetch, mock_extract = mock_trafilatura
    
    # Test with invalid URL
    with pytest.raises(ValueError) as excinfo:
        app.extract_content("invalid-url")
    
    assert "Invalid URL provided" in str(excinfo.value)
    mock_fetch.assert_not_called()
    mock_extract.assert_not_called()

def test_extract_content_fetch_failure(mock_trafilatura):
    mock_fetch, mock_extract = mock_trafilatura
    
    # Mock fetch failure
    mock_fetch.return_value = None
    
    # Test with fetch failure
    with pytest.raises(ValueError) as excinfo:
        app.extract_content("https://example.com")
    
    assert "Failed to download content" in str(excinfo.value)
    mock_fetch.assert_called_once_with("https://example.com")
    mock_extract.assert_not_called()

def test_extract_content_extraction_failure(mock_trafilatura):
    mock_fetch, mock_extract = mock_trafilatura
    
    # Mock extraction failure
    mock_fetch.return_value = "<html><body>Test</body></html>"
    mock_extract.return_value = None
    
    # Test with extraction failure
    with pytest.raises(ValueError) as excinfo:
        app.extract_content("https://example.com")
    
    assert "Failed to extract content" in str(excinfo.value)
    mock_fetch.assert_called_once_with("https://example.com")
    mock_extract.assert_called_once()

def test_generate_summary_success(mock_bedrock_client):
    # Mock successful Bedrock response
    mock_response = {
        'body': MagicMock()
    }
    mock_response['body'].read.return_value = json.dumps({
        "results": [{"outputText": "This is a summary."}]
    })
    mock_bedrock_client.invoke_model.return_value = mock_response
    
    # Call the function
    result = app.generate_summary("Test content", "Summarize this", "test-model")
    
    # Verify the result
    assert result == "This is a summary."
    mock_bedrock_client.invoke_model.assert_called_once()

def test_generate_summary_api_error(mock_bedrock_client):
    # Mock Bedrock API error
    error_response = {
        'Error': {
            'Code': 'ValidationException',
            'Message': 'Invalid model ID'
        }
    }
    mock_bedrock_client.invoke_model.side_effect = ClientError(
        error_response=error_response,
        operation_name='InvokeModel'
    )
    
    # Test with API error
    with pytest.raises(Exception) as excinfo:
        app.generate_summary("Test content", "Summarize this", "invalid-model")
    
    assert "Bedrock API error" in str(excinfo.value)
    mock_bedrock_client.invoke_model.assert_called_once()

def test_lambda_handler_success(mock_trafilatura, mock_bedrock_client):
    mock_fetch, mock_extract = mock_trafilatura
    
    # Mock successful content extraction
    mock_fetch.return_value = "<html><body><h1>Test Content</h1><p>This is a test.</p></body></html>"
    mock_extract.return_value = "# Test Content\n\nThis is a test."
    
    # Mock successful Bedrock response
    mock_response = {
        'body': MagicMock()
    }
    mock_response['body'].read.return_value = json.dumps({
        "results": [{"outputText": "This is a summary."}]
    })
    mock_bedrock_client.invoke_model.return_value = mock_response
    
    # Create test event
    event = {
        "body": json.dumps({
            "url": "https://example.com",
            "prompt": "Summarize this",
            "model": "test-model"
        })
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Verify the response
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["url"] == "https://example.com"
    assert body["extracted_content"] == "# Test Content\n\nThis is a test."
    assert body["summary"] == "This is a summary."
    assert body["model_used"] == "test-model"
    assert "processing_time" in body

def test_lambda_handler_missing_url():
    # Create test event with missing URL
    event = {
        "body": json.dumps({
            "prompt": "Summarize this",
            "model": "test-model"
        })
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Verify the response
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
    assert "Missing required parameter" in body["error"]

def test_lambda_handler_extraction_error(mock_trafilatura):
    mock_fetch, mock_extract = mock_trafilatura
    
    # Mock extraction failure
    mock_fetch.side_effect = Exception("Network error")
    
    # Create test event
    event = {
        "body": json.dumps({
            "url": "https://example.com",
            "prompt": "Summarize this",
            "model": "test-model"
        })
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Verify the response
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
    assert "Content extraction failed" in body["error"]