import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize Cognito client with a default region
# The region will be overridden by AWS_REGION environment variable when deployed
region = os.environ.get('AWS_REGION', 'us-east-1')
cognito = boto3.client('cognito-idp', region_name=region)

def lambda_handler(event, context):
    """
    Lambda handler for user endpoints.
    GET /users - List all users
    GET /users/{username} - Get specific user details
    """
    # Extract path parameters and query string parameters
    path_parameters = event.get('pathParameters', {})
    if path_parameters is None:
        path_parameters = {}
    
    # Get the username if provided in the path
    username = path_parameters.get('username')
    
    # Check if this is a request for a specific user or all users
    if username:
        return get_user(username)
    else:
        return list_users()

def list_users():
    """List all users in the Cognito User Pool"""
    try:
        # Get the User Pool ID from environment variable
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        # Call Cognito to list users
        response = cognito.list_users(
            UserPoolId=user_pool_id,
            Limit=60
        )
        
        # Extract relevant user information
        users = []
        for user in response.get('Users', []):
            user_data = {
                'username': user.get('Username'),
                'enabled': user.get('Enabled'),
                'status': user.get('UserStatus'),
                'created': user.get('UserCreateDate').isoformat() if user.get('UserCreateDate') else None,
                'attributes': {attr['Name']: attr['Value'] for attr in user.get('Attributes', [])}
            }
            users.append(user_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'users': users,
                'count': len(users)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def get_user(username):
    """Get details for a specific user"""
    try:
        # Get the User Pool ID from environment variable
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        # Call Cognito to get user
        response = cognito.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        
        # Extract user attributes
        attributes = {attr['Name']: attr['Value'] for attr in response.get('UserAttributes', [])}
        
        # Create user object
        user = {
            'username': response.get('Username'),
            'enabled': response.get('Enabled'),
            'status': response.get('UserStatus'),
            'created': response.get('UserCreateDate').isoformat() if response.get('UserCreateDate') else None,
            'lastModified': response.get('UserLastModifiedDate').isoformat() if response.get('UserLastModifiedDate') else None,
            'attributes': attributes
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(user)
        }
    except ClientError as e:
        # Check if this is a UserNotFoundException
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f"User '{username}' not found"
                })
            }
        # Handle other ClientErrors
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }