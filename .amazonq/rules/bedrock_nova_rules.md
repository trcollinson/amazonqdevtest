# Amazon Bedrock Nova Model Rules

## Using Nova Models in Lambda Functions

When implementing Lambda functions that use Amazon Bedrock Nova models, follow these guidelines:

### Environment Variables
- Always include these environment variables in your SAM template:
  ```yaml
  Environment:
    Variables:
      BEDROCK_REGION: !Ref AWS::Region
      DEFAULT_MODEL: amazon.nova-pro-v1:0  # Or your preferred Nova model
      INFERENCE_PROFILE_ARN: <your-inference-profile-arn>  # Required for Nova models
  ```

### IAM Permissions
- Include these permissions in your Lambda function policy:
  ```yaml
  Policies:
    - Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - bedrock:InvokeModel
            - bedrock:ListFoundationModels
            - bedrock:ListInferenceProfiles
            - bedrock:CreateInferenceProfile
          Resource: '*'
  ```

### Request Format
- Nova models require a specific message format with content array:
  ```python
  # Correct format for Nova models
  request_body = {
      "messages": [
          {
              "role": "user",
              "content": [
                  {
                      "text": your_prompt
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
  ```

### Response Parsing
- Parse Nova model responses correctly:
  ```python
  response_body = json.loads(response.get('body').read())
  summary = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
  ```

### Inference Profiles
- Nova models require an inference profile:
  ```python
  # Check if using a Nova model
  if "nova" in model.lower() and not (model.startswith('arn:') or ':inference-profile/' in model):
      # Use a pre-configured inference profile ARN if available
      if INFERENCE_PROFILE_ARN:
          model = INFERENCE_PROFILE_ARN
      else:
          # Otherwise, find or create an inference profile
          # (See implementation details in the code)
  ```

### Model-Specific Logic
- Always include model-specific logic for request formatting:
  ```python
  if "nova" in model.lower():
      # Nova-specific request format
  else:
      # Default format for other models
  ```

Following these rules will ensure consistent implementation of Lambda functions that use Nova models across the project.