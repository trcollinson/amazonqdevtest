# SAM API Project

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI.

## Project Structure

- `hello_world/` - Code for the application's Lambda function.
- `template.yaml` - A template that defines the application's AWS resources.
- `samconfig.toml` - Configuration file for the SAM CLI.

## Deploy the application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS.

## API Endpoints

- GET /hello - Returns a Hello World message

## Adding New Endpoints

To add new endpoints to this API:

1. Define new functions in the `template.yaml` file
2. Create corresponding handlers in separate directories
3. Run `sam build` and `sam deploy` to update your deployment