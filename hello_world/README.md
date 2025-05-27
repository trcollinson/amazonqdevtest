# Hello World Lambda Function

This directory contains the Lambda function code for the Hello World API endpoint.

## Contents

- `app.py` - The main Lambda handler function that processes API Gateway requests
- `requirements.txt` - Python dependencies required by this function
- `__init__.py` - Makes the directory a proper Python package

## Usage

The Lambda function in this directory:

1. Receives API Gateway events with Cognito authorization
2. Extracts user information from Cognito claims
3. Returns a personalized greeting with the user's email

## Adding Functionality

When extending this function:
- Keep the handler signature compatible with API Gateway events
- Maintain the response format with statusCode and body
- Process Cognito claims consistently for user identification