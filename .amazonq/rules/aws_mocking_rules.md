# AWS Mocking Rules

## Proper Exception Handling in AWS Service Tests

When mocking AWS service exceptions in tests, always follow these guidelines:

- Use `botocore.exceptions.ClientError` for all AWS service-specific exceptions
- Structure error responses correctly with the proper format:
  ```python
  error_response = {
      'Error': {
          'Code': 'ServiceSpecificErrorCode',
          'Message': 'Error message'
      }
  }
  ```
- Mock exceptions with the correct operation name:
  ```python
  ClientError(error_response=error_response, operation_name='OperationName')
  ```
- Never create mock exception classes that don't inherit from BaseException
- Import the necessary exception classes at the top of the test file:
  ```python
  from botocore.exceptions import ClientError
  ```

This rule ensures that AWS service exceptions are mocked correctly in tests, preventing issues like "TypeError: catching classes that do not inherit from BaseException is not allowed".