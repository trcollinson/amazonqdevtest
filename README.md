# SAM API Project with Cognito Authentication

This project contains source code and supporting files for a serverless application with Cognito authentication that you can deploy with the SAM CLI.

## Project Structure

- `hello_world/` - Code for the Hello World Lambda function
- `users/` - Code for the Users API endpoints
- `template.yaml` - A template that defines the application's AWS resources
- `samconfig.toml` - Configuration file for the SAM CLI
- `tests/` - Unit tests for the application

## API Endpoints

- **GET /hello** - Returns a Hello World message (requires authentication)
- **GET /users** - Lists all users in the Cognito User Pool (requires authentication)
- **GET /users/{username}** - Gets detailed information about a specific user (requires authentication)

## Deploy the application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS.

## Authentication

The API is secured with Amazon Cognito. To access the endpoints, you need to:

1. Create a user in the Cognito User Pool
2. Authenticate and get an ID token
3. Include the ID token in the Authorization header of your requests

### Creating a User

```bash
# Replace USER_POOL_ID with the value from the stack outputs
aws cognito-idp admin-create-user \
  --user-pool-id USER_POOL_ID \
  --username user@example.com \
  --temporary-password Temp123! \
  --user-attributes Name=email,Value=user@example.com

# Set a permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id USER_POOL_ID \
  --username user@example.com \
  --password YourPassword123! \
  --permanent
```

### Getting an Authentication Token

```bash
# Replace USER_POOL_ID and CLIENT_ID with values from the stack outputs
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id CLIENT_ID \
  --auth-parameters USERNAME=user@example.com,PASSWORD=YourPassword123!
```

This will return an ID token that you can use to authenticate API requests.

### Making Authenticated Requests

```bash
# Replace API_URL with the API endpoint value from stack outputs
# Replace ID_TOKEN with the token from the previous step
curl -H "Authorization: ID_TOKEN" API_URL
```

## Testing

Run the unit tests with:

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run tests (includes coverage report)
pytest tests/
```

The test command will automatically generate a coverage report in the terminal and an HTML report in the `htmlcov` directory.

To view the HTML coverage report, open `htmlcov/index.html` in your browser.