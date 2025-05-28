import json
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Import the app module directly using the file path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock boto3 client before importing app
with patch('boto3.client') as mock_boto:
    from users import app

@pytest.fixture
def mock_cognito():
    with patch('users.app.cognito') as mock:
        yield mock

def test_list_users(mock_cognito):
    # Mock Cognito response
    mock_cognito.list_users.return_value = {
        'Users': [
            {
                'Username': 'user1@example.com',
                'Enabled': True,
                'UserStatus': 'CONFIRMED',
                'UserCreateDate': MagicMock(isoformat=lambda: '2023-01-01T00:00:00'),
                'Attributes': [
                    {'Name': 'email', 'Value': 'user1@example.com'},
                    {'Name': 'name', 'Value': 'Test User 1'}
                ]
            },
            {
                'Username': 'user2@example.com',
                'Enabled': True,
                'UserStatus': 'CONFIRMED',
                'UserCreateDate': MagicMock(isoformat=lambda: '2023-01-02T00:00:00'),
                'Attributes': [
                    {'Name': 'email', 'Value': 'user2@example.com'},
                    {'Name': 'name', 'Value': 'Test User 2'}
                ]
            }
        ]
    }
    
    # Mock environment variable
    with patch.dict(os.environ, {'USER_POOL_ID': 'test-pool-id'}):
        # Create mock event
        event = {
            'httpMethod': 'GET',
            'path': '/users',
            'pathParameters': None
        }
        
        # Call the lambda handler
        response = app.lambda_handler(event, None)
        
        # Assert response structure
        assert response['statusCode'] == 200
        
        # Parse the body as JSON
        body = json.loads(response['body'])
        
        # Assert the response content
        assert 'users' in body
        assert 'count' in body
        assert body['count'] == 2
        assert len(body['users']) == 2
        assert body['users'][0]['username'] == 'user1@example.com'
        assert body['users'][0]['attributes']['email'] == 'user1@example.com'
        assert body['users'][0]['attributes']['name'] == 'Test User 1'

def test_get_user(mock_cognito):
    # Mock Cognito response
    mock_cognito.admin_get_user.return_value = {
        'Username': 'user1@example.com',
        'Enabled': True,
        'UserStatus': 'CONFIRMED',
        'UserCreateDate': MagicMock(isoformat=lambda: '2023-01-01T00:00:00'),
        'UserLastModifiedDate': MagicMock(isoformat=lambda: '2023-01-03T00:00:00'),
        'UserAttributes': [
            {'Name': 'email', 'Value': 'user1@example.com'},
            {'Name': 'name', 'Value': 'Test User 1'},
            {'Name': 'custom:role', 'Value': 'admin'}
        ]
    }
    
    # Mock environment variable
    with patch.dict(os.environ, {'USER_POOL_ID': 'test-pool-id'}):
        # Create mock event
        event = {
            'httpMethod': 'GET',
            'path': '/users/user1@example.com',
            'pathParameters': {
                'username': 'user1@example.com'
            }
        }
        
        # Call the lambda handler
        response = app.lambda_handler(event, None)
        
        # Assert response structure
        assert response['statusCode'] == 200
        
        # Parse the body as JSON
        body = json.loads(response['body'])
        
        # Assert the response content
        assert body['username'] == 'user1@example.com'
        assert body['enabled'] == True
        assert body['status'] == 'CONFIRMED'
        assert body['attributes']['email'] == 'user1@example.com'
        assert body['attributes']['name'] == 'Test User 1'
        assert body['attributes']['custom:role'] == 'admin'

def test_get_user_not_found(mock_cognito):
    # Create a proper ClientError exception for UserNotFoundException
    error_response = {
        'Error': {
            'Code': 'UserNotFoundException',
            'Message': 'User does not exist'
        }
    }
    
    # Use ClientError which is a proper exception class
    mock_cognito.admin_get_user.side_effect = ClientError(
        error_response=error_response,
        operation_name='AdminGetUser'
    )
    
    # Mock environment variable
    with patch.dict(os.environ, {'USER_POOL_ID': 'test-pool-id'}):
        # Create mock event
        event = {
            'httpMethod': 'GET',
            'path': '/users/nonexistent@example.com',
            'pathParameters': {
                'username': 'nonexistent@example.com'
            }
        }
        
        # Call the lambda handler
        response = app.lambda_handler(event, None)
        
        # Assert response structure
        assert response['statusCode'] == 404
        
        # Parse the body as JSON
        body = json.loads(response['body'])
        
        # Assert the error message
        assert 'error' in body
        assert "not found" in body['error']