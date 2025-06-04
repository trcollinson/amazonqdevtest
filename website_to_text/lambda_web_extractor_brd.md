# AWS Lambda Web Content Extractor - Business Requirements Document

## Project Overview

**Objective:** Create an AWS Lambda function that accepts a website URL, extracts and converts the content to LLM-readable format, and generates AI-powered summaries using Amazon Bedrock.

**Primary Use Case:** Enable automated content summarization from any web page through a serverless API endpoint.

## Functional Requirements

### Core Functionality

#### 1. Web Content Extraction
- **Input:** Website URL via Lambda event (API Gateway, direct invocation, etc.)
- **Processing:** Use `trafilatura` library to automatically extract main article content
- **Output:** Clean, structured content ready for LLM processing
- **Error Handling:** Handle invalid URLs, network timeouts, and extraction failures

#### 2. Content Formatting
- **Format:** Convert extracted content to Markdown format for optimal LLM consumption
- **Structure Preservation:** Maintain headings, lists, and basic formatting from original content
- **Content Optimization:** Ensure content fits within LLM context windows
- **Cleanup:** Remove any remaining HTML artifacts or unwanted elements

#### 3. LLM Integration via Amazon Bedrock
- **Service:** Amazon Bedrock API integration
- **Model Selection:** Configurable LLM model (Amazon Nova, Titan, etc.)
- **Prompt Engineering:** Accept custom prompts for different summarization needs
- **Response Handling:** Return structured LLM responses with error handling

## Technical Requirements

### Architecture Components

#### Lambda Function Structure
```
lambda_function.py
├── extract_content(url) -> markdown_content
├── generate_summary(content, prompt) -> llm_response
└── lambda_handler(event, context) -> api_response
```

#### Required Dependencies
- `trafilatura` - Web content extraction
- `boto3` - AWS SDK for Bedrock integration
- `requests` - HTTP client (if needed beyond trafilatura)
- Standard Python libraries for JSON, logging, error handling

#### AWS Services Integration
- **AWS Lambda** - Main compute service
- **Amazon Bedrock** - LLM inference
- **API Gateway** (optional) - REST API endpoint
- **CloudWatch** - Logging and monitoring

### Input/Output Specifications

#### Lambda Event Input
```json
{
  "url": "https://example.com/article",
  "prompt": "Provide a concise summary of the main points",
  "model": "amazon.nova-pro-v1:0" // optional, with default
}
```

#### Lambda Response Output
```json
{
  "statusCode": 200,
  "body": {
    "url": "https://example.com/article",
    "extracted_content": "# Article Title\n\nMain content...",
    "summary": "AI-generated summary based on prompt",
    "model_used": "amazon.nova-pro-v1:0",
    "processing_time": 2.3
  }
}
```

#### Error Response Format
```json
{
  "statusCode": 400,
  "body": {
    "error": "Content extraction failed",
    "details": "Unable to extract content from provided URL",
    "url": "https://example.com/article"
  }
}
```

## Implementation Approach

### Phase 1: Content Extraction
1. Implement URL validation and sanitization
2. Use `trafilatura.fetch_url()` for one-step content extraction
3. Convert extracted content to Markdown format
4. Add content length validation for LLM context limits
5. Implement comprehensive error handling

### Phase 2: LLM Integration
1. Configure AWS Bedrock client with proper IAM permissions
2. Implement prompt templating system
3. Add model selection logic with fallback options
4. Implement response parsing and validation
5. Add retry logic for API failures

### Phase 3: Integration & Testing
1. Combine extraction and LLM functions in main handler
2. Implement end-to-end error handling
3. Add logging and monitoring
4. Performance optimization and testing

## Configuration Requirements

### Environment Variables
- `BEDROCK_REGION` - AWS region for Bedrock service
- `DEFAULT_MODEL` - Default LLM model identifier
- `MAX_CONTENT_LENGTH` - Maximum content length for processing
- `TIMEOUT_SECONDS` - Request timeout configuration

### IAM Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## Success Criteria

### Performance Targets
- **Response Time:** < 30 seconds for typical web pages
- **Success Rate:** > 95% for accessible web content
- **Error Handling:** Graceful degradation with informative error messages

### Quality Metrics
- Successfully extract main content from diverse website layouts
- Generate relevant summaries based on provided prompts
- Maintain content structure and readability in Markdown format

## Constraints & Assumptions

### Technical Constraints
- AWS Lambda timeout limits (15 minutes maximum)
- Memory constraints for large web pages
- Network connectivity requirements for external URLs
- Bedrock API rate limits and quotas

### Assumptions
- Input URLs point to publicly accessible web content
- Content is primarily text-based (not multimedia-heavy)
- Users will provide reasonable prompts for summarization
- AWS Bedrock service availability in target regions

## Risk Mitigation

### Content Extraction Risks
- **Mitigation:** Implement fallback extraction methods
- **Monitoring:** Track extraction success rates by domain

### LLM API Risks
- **Mitigation:** Implement retry logic and circuit breakers
- **Fallback:** Queue failed requests for later processing

### Security Considerations
- Validate and sanitize all input URLs
- Implement rate limiting to prevent abuse
- Log access patterns for security monitoring

## Future Enhancements

### Potential Features
- Batch processing of multiple URLs
- Content caching to reduce processing time
- Support for authenticated content
- Custom extraction rules for specific domains
- Integration with other AWS services (S3 storage, SQS queuing)

---

**Document Version:** 1.0  
**Last Updated:** June 2025  
**Status:** Ready for Development