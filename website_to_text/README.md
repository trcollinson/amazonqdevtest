# Website to Text Lambda Function

This Lambda function extracts content from a website URL, converts it to a clean markdown format, and generates an AI-powered summary using Amazon Bedrock.

## Features

- Extracts main content from web pages using the `trafilatura` library
- Converts content to markdown format for optimal LLM consumption
- Generates summaries using Amazon Bedrock models
- Handles errors gracefully with informative messages

## API Endpoint

### Request Format

```json
{
  "url": "https://example.com/article",
  "prompt": "Provide a concise summary of the main points",
  "model": "amazon.titan-text-express-v1"
}
```

### Response Format

```json
{
  "url": "https://example.com/article",
  "extracted_content": "# Article Title\n\nMain content...",
  "summary": "AI-generated summary based on prompt",
  "model_used": "amazon.titan-text-express-v1",
  "processing_time": 2.3
}
```

## Environment Variables

- `BEDROCK_REGION` - AWS region for Bedrock service (default: us-east-1)
- `DEFAULT_MODEL` - Default LLM model identifier (default: amazon.nova-pro-v1:0)
- `MAX_CONTENT_LENGTH` - Maximum content length for processing (default: 10000)
- `TIMEOUT_SECONDS` - Request timeout configuration (default: 30)
- `INFERENCE_PROFILE_ARN` - ARN of the Bedrock inference profile to use for Nova models
- `DEFAULT_INFERENCE_PROFILE_NAME` - Name to use when creating a new inference profile (default: nova-default-profile)

## Required IAM Permissions

- `bedrock:InvokeModel`
- `bedrock:ListFoundationModels`
- Standard Lambda logging permissions