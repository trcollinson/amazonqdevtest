import json
import time
import os
import logging
import boto3
import trafilatura
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables with defaults
BEDROCK_REGION = os.environ.get('BEDROCK_REGION', 'us-east-1')
DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'amazon.nova-pro-v1:0')  # Back to Nova as default
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10000))
TIMEOUT_SECONDS = int(os.environ.get('TIMEOUT_SECONDS', 30))
INFERENCE_PROFILE_ARN = os.environ.get('INFERENCE_PROFILE_ARN', '')  # For specifying inference profile directly
DEFAULT_INFERENCE_PROFILE_NAME = os.environ.get('DEFAULT_INFERENCE_PROFILE_NAME', 'nova-default-profile')  # Default profile name

def extract_content(url):
    """
    Extract content from a website URL and convert to markdown format
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: Extracted content in markdown format
        
    Raises:
        ValueError: If URL is invalid or content extraction fails
    """
    if not url or not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL provided")
    
    try:
        # Download and extract the main content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError("Failed to download content from URL")
        
        # Extract the main content and convert to markdown
        result = trafilatura.extract(downloaded, output_format='markdown', 
                                    include_links=True, include_images=False,
                                    include_tables=True)
        
        if not result:
            raise ValueError("Failed to extract content from downloaded page")
        
        # Truncate if content is too long
        if len(result) > MAX_CONTENT_LENGTH:
            result = result[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length]"
            
        return result
        
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        raise ValueError(f"Content extraction failed: {str(e)}")

def generate_summary(content, prompt, model=None):
    """
    Generate a summary of the content using Amazon Bedrock
    
    Args:
        content (str): The content to summarize
        prompt (str): The prompt to use for summarization
        model (str, optional): The model ID or inference profile ARN to use
        
    Returns:
        str: The generated summary
        
    Raises:
        Exception: If the Bedrock API call fails
    """
    if not model:
        model = DEFAULT_MODEL
    
    try:
        # Initialize Bedrock client
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=BEDROCK_REGION
        )
        
        # Prepare the prompt with content
        full_prompt = f"{prompt}\n\nContent:\n{content}"
        
        # Prepare request body based on model
        if "nova" in model.lower():
            # Nova models use a specific message format
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
        else:
            # Default format for other models like Titan
            request_body = {
                "inputText": full_prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 1000,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
        
        # For Nova models, we need to use a specific inference profile
        if "nova" in model.lower() and not (model.startswith('arn:') or ':inference-profile/' in model):
            try:
                # First check if inference profile ARN is provided
                if INFERENCE_PROFILE_ARN:
                    logger.info(f"Using configured inference profile ARN: {INFERENCE_PROFILE_ARN}")
                    model = INFERENCE_PROFILE_ARN
                else:
                    # Try to list available inference profiles
                    bedrock_mgmt = boto3.client('bedrock', region_name=BEDROCK_REGION)
                    profiles = bedrock_mgmt.list_inference_profiles()
                    
                    # Look for an existing Nova profile
                    nova_profile = None
                    for profile in profiles.get('inferenceProfiles', []):
                        if 'nova' in profile['name'].lower():
                            nova_profile = profile['inferenceProfileArn']
                            break
                    
                    if nova_profile:
                        logger.info(f"Found existing Nova inference profile: {nova_profile}")
                        model = nova_profile
                    else:
                        # If no profile found, try to create one
                        try:
                            # Get account ID
                            sts_client = boto3.client('sts')
                            account_id = sts_client.get_caller_identity()['Account']
                            
                            # Create inference profile
                            response = bedrock_mgmt.create_inference_profile(
                                inferenceProfileName=DEFAULT_INFERENCE_PROFILE_NAME,
                                modelArn=f"arn:aws:bedrock:{BEDROCK_REGION}::foundation-model/{model}",
                                provisionedModelThroughput=1
                            )
                            
                            # Use the newly created profile
                            model = response['inferenceProfileArn']
                            logger.info(f"Created new inference profile: {model}")
                        except Exception as create_error:
                            logger.error(f"Failed to create inference profile: {str(create_error)}")
                            raise Exception(f"Nova model requires an inference profile. Please create one in the Bedrock console or set INFERENCE_PROFILE_ARN environment variable.")
            except Exception as e:
                logger.error(f"Error handling inference profile: {str(e)}")
                raise Exception(f"Nova model requires an inference profile: {str(e)}")
        
        # Invoke the model
        start_time = time.time()
        response = bedrock_client.invoke_model(
            modelId=model,
            body=json.dumps(request_body)
        )
        
        # Parse the response based on model
        response_body = json.loads(response.get('body').read())
        if "nova" in model.lower():
            # Nova models return content in a different nested structure
            summary = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
        else:
            # Default format for other models like Titan
            summary = response_body.get('results', [{}])[0].get('outputText', '')
        
        return summary.strip()
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"Bedrock API error: {error_code} - {error_message}")
        raise Exception(f"Bedrock API error: {error_message}")
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise Exception(f"Summary generation failed: {str(e)}")

def lambda_handler(event, context):
    """
    Lambda handler function
    
    Args:
        event (dict): Lambda event
        context (object): Lambda context
        
    Returns:
        dict: API response
    """
    start_time = time.time()
    
    try:
        # Extract parameters from the event
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        url = body.get('url')
        prompt = body.get('prompt', 'Provide a concise summary of the main points')
        model = body.get('model', DEFAULT_MODEL)
        
        if not url:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required parameter",
                    "details": "URL parameter is required"
                })
            }
        
        # Extract content from the URL
        extracted_content = extract_content(url)
        
        # Generate summary using Bedrock
        summary = generate_summary(extracted_content, prompt, model)
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        # Return successful response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "url": url,
                "extracted_content": extracted_content,
                "summary": summary,
                "model_used": model,
                "processing_time": processing_time
            })
        }
        
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Content extraction failed",
                "details": str(e),
                "url": body.get('url') if 'body' in locals() and isinstance(body, dict) else None
            })
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e),
                "url": body.get('url') if 'body' in locals() and isinstance(body, dict) else None
            })
        }