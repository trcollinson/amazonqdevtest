# S3 Upload Signed URL Generator

This Lambda function generates pre-signed URLs for direct uploads to S3 from client applications.

## Features

- Generates secure pre-signed URLs for S3 uploads
- Creates unique file keys to prevent overwriting
- Configurable URL expiration time
- Supports content type specification
- Returns file metadata along with the URL

## API Endpoint

### Request Format

```json
{
  "file_name": "example.jpg",
  "content_type": "image/jpeg"
}
```

### Response Format

```json
{
  "signed_url": "https://bucket-name.s3.amazonaws.com/uploads/uuid.jpg?AWSAccessKeyId=...",
  "file_key": "uploads/uuid.jpg",
  "bucket": "user-uploads-bucket",
  "expiration_seconds": 300,
  "max_size": 10485760
}
```

## Environment Variables

- `BUCKET_NAME` - S3 bucket name for uploads (default: user-uploads-bucket)
- `URL_EXPIRATION_SECONDS` - Expiration time for signed URLs in seconds (default: 300)
- `MAX_UPLOAD_SIZE_MB` - Maximum allowed upload size in MB (default: 10)

## Required IAM Permissions

- `s3:PutObject` on the target bucket
- Standard Lambda logging permissions