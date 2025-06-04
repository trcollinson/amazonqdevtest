import json
import os
import boto3
import uuid
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables with defaults
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'user-uploads-bucket')
EXPIRATION = int(os.environ.get('URL_EXPIRATION_SECONDS', 300))  # 5 minutes default
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE_MB', 10)) * 1024 * 1024  # Convert MB to bytes

def generate_signed_url(file_name, content_type):
    """
    Generate a pre-signed URL for uploading a file to S3
    
    Args:
        file_name (str): Original file name
        content_type (str): MIME type of the file
        
    Returns:
        dict: Dictionary containing the signed URL and upload details
        
    Raises:
        Exception: If URL generation fails
    """
    try:
        # Generate a unique key for the file
        file_extension = os.path.splitext(file_name)[1] if '.' in file_name else ''
        # Strip any leading dots from the extension
        file_extension = file_extension.lstrip('.')
        # Add the dot back only if there's an extension
        if file_extension:
            file_extension = f".{file_extension}"
        unique_key = f"uploads/{uuid.uuid4()}{file_extension}"
        
        # Log the bucket name and key for debugging
        logger.info(f"Generating pre-signed URL for bucket: {BUCKET_NAME}, key: {unique_key}")
        
        # Use boto3 client with explicit region and virtual addressing style
        region = os.environ.get('AWS_REGION', 'us-east-1')
        config = boto3.session.Config(s3={'addressing_style': 'virtual'})
        s3_client = boto3.client('s3', region_name=region, config=config)
        
        signed_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': unique_key,
                'ContentType': content_type
            },
            ExpiresIn=EXPIRATION
        )
        
        # Log the final URL and key for debugging
        logger.info(f"Generated pre-signed URL for key: {unique_key}")
        
        return {
            'signed_url': signed_url,
            'file_key': unique_key,
            'bucket': BUCKET_NAME,
            'content_type': content_type,
            'expiration_seconds': EXPIRATION,
            'max_size': MAX_UPLOAD_SIZE
        }
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"S3 error: {error_code} - {error_message}")
        raise Exception(f"Failed to generate signed URL: {error_message}")
    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}")
        raise Exception(f"Failed to generate signed URL: {str(e)}")

def lambda_handler(event, context):
    """
    Lambda handler function
    
    Args:
        event (dict): Lambda event
        context (object): Lambda context
        
    Returns:
        dict: API response
    """
    try:
        # Extract parameters from the event
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        file_name = body.get('file_name')
        content_type = body.get('content_type', 'application/octet-stream')
        
        if not file_name:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required parameter",
                    "details": "file_name parameter is required"
                })
            }
        
        # Generate signed URL
        result = generate_signed_url(file_name, content_type)
        
        # Return successful response
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e)
            })
        }