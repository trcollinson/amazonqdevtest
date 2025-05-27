import json
import pytest
import sys
import os

# Import the app module directly using the file path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hello_world import app

def test_lambda_handler():
    # Mock API Gateway event
    event = {
        "httpMethod": "GET",
        "path": "/hello",
        "headers": {},
        "queryStringParameters": None,
        "body": None
    }
    
    # Call the lambda handler
    response = app.lambda_handler(event, None)
    
    # Assert response structure
    assert response["statusCode"] == 200
    
    # Parse the body as JSON
    body = json.loads(response["body"])
    
    # Assert the message
    assert "message" in body
    assert body["message"] == "Hello World!"