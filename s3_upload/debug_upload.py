import boto3
import uuid
import os
import json

# This is a debug script to test S3 uploads directly
# Run this locally with AWS credentials configured

# Replace with your bucket name
BUCKET_NAME = "user-uploads-YOUR-ACCOUNT-ID-YOUR-REGION"

def test_presigned_url():
    """Test generating and using a pre-signed URL"""
    
    # Create a unique file key
    unique_key = f"uploads/test-{uuid.uuid4()}.txt"
    
    # Create test content
    test_content = "This is a test file for S3 upload."
    
    # Create S3 client
    s3_client = boto3.client('s3')
    
    # Generate pre-signed URL
    print(f"Generating pre-signed URL for bucket: {BUCKET_NAME}, key: {unique_key}")
    signed_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': unique_key,
            'ContentType': 'text/plain'
        },
        ExpiresIn=300,
        HttpMethod='PUT'
    )
    
    print(f"Pre-signed URL: {signed_url}")
    
    # Use the pre-signed URL to upload content
    import requests
    
    print("Uploading content using pre-signed URL...")
    response = requests.put(
        signed_url,
        data=test_content,
        headers={'Content-Type': 'text/plain'}
    )
    
    print(f"Upload response status code: {response.status_code}")
    if response.status_code >= 300:
        print(f"Error response: {response.text}")
    else:
        print("Upload successful!")
        print(f"File URL: https://{BUCKET_NAME}.s3.amazonaws.com/{unique_key}")

if __name__ == "__main__":
    test_presigned_url()