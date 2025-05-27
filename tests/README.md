# Tests Directory

This directory contains all tests for the SAM API project.

## Contents

- `test_hello_world.py` - Unit tests for the Hello World Lambda function
- `requirements.txt` - Test dependencies including pytest and pytest-cov
- `conftest.py` - Pytest configuration for the test suite
- `__init__.py` - Makes the directory a proper Python package

## Usage

The tests in this directory:

1. Verify the functionality of Lambda functions
2. Mock API Gateway events and Cognito claims
3. Generate coverage reports to ensure code quality

## Adding Tests

When adding tests for new endpoints:
- Follow the existing pattern in `test_hello_world.py`
- Mock the API Gateway event structure with appropriate Cognito claims
- Verify both the response structure and content
- Ensure high code coverage for all code paths