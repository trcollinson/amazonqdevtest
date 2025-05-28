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
    POST /users - Create a new user
    """
    # Get HTTP method
    http_method = event.get('httpMethod', '')
    
    # Extract path parameters and query string parameters
    path_parameters = event.get('pathParameters', {})
    if path_parameters is None:
        path_parameters = {}
    
    # Get the username if provided in the path
    username = path_parameters.get('username')
    
    # Route the request based on HTTP method and path
    if http_method == 'GET':
        if username:
            return get_user(username)
        else:
            return list_users()
    elif http_method == 'POST':
        # Parse the request body for user creation
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid JSON in request body'
                })
            }
        return create_user(body)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({
                'error': f'Method {http_method} not allowed'
            })
        }

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

def create_user(user_data):
    """Create a new user in Cognito User Pool"""
    try:
        # Get required parameters
        email = user_data.get('email')
        password = user_data.get('password')
        name = user_data.get('name', '')
        
        # Validate required fields
        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Email and password are required'
                })
            }
        
        # Get the User Pool ID and Client ID from environment variables
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        # Prepare user attributes
        user_attributes = [
            {'Name': 'email', 'Value': email},
            {'Name': 'email_verified', 'Value': 'true'}
        ]
        
        if name:
            user_attributes.append({'Name': 'name', 'Value': name})
        
        # Add any additional attributes from the request
        for key, value in user_data.items():
            if key not in ['email', 'password', 'name'] and value:
                # For custom attributes, prefix with 'custom:'
                if not key.startswith('custom:') and not key in ['given_name', 'family_name', 'phone_number']:
                    attr_name = f'custom:{key}'
                else:
                    attr_name = key
                user_attributes.append({'Name': attr_name, 'Value': str(value)})
        
        # Create the user
        response = cognito.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=user_attributes,
            MessageAction='SUPPRESS',  # Don't send welcome email
            TemporaryPassword=password
        )
        
        # Set the password as permanent (no reset required)
        cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=email,
            Password=password,
            Permanent=True
        )
        
        # Extract user data from response
        user = response.get('User', {})
        user_attributes = {attr['Name']: attr['Value'] for attr in user.get('Attributes', [])}
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'username': user.get('Username'),
                'status': user.get('UserStatus'),
                'created': user.get('UserCreateDate').isoformat() if user.get('UserCreateDate') else None,
                'attributes': user_attributes,
                'message': 'User created successfully'
            })
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'UsernameExistsException':
            return {
                'statusCode': 409,
                'body': json.dumps({
                    'error': f"User with email '{email}' already exists"
                })
            }
        elif error_code == 'InvalidPasswordException':
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': error_message
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': f"{error_code}: {error_message}"
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }