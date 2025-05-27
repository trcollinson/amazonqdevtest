import json

def lambda_handler(event, context):
    # Access the Cognito claims from the event
    claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
    
    # Get the user's email from the claims
    user_email = claims.get('email', 'unknown user')
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Hello {user_email}!",
        }),
    }