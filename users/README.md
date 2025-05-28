# Users API Endpoint

This directory contains the Lambda function code for the Users API endpoints that interact with Amazon Cognito.

## Contents

- `app.py` - The main Lambda handler function that processes API Gateway requests for user operations
- `requirements.txt` - Python dependencies required by this function
- `__init__.py` - Makes the directory a proper Python package

## Endpoints

This Lambda function handles two endpoints:

1. **GET /users** - Lists all users in the Cognito User Pool
   - Returns a list of users with their basic information and attributes
   - Requires Cognito authentication

2. **GET /users/{username}** - Gets detailed information about a specific user
   - Returns comprehensive information about the specified user
   - Requires Cognito authentication
   - Returns 404 if the user is not found

## Environment Variables

The function requires the following environment variables:

- `USER_POOL_ID` - The ID of the Cognito User Pool to query

## IAM Permissions

The function requires the following IAM permissions:
- `cognito-idp:ListUsers`
- `cognito-idp:AdminGetUser`