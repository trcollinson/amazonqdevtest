import pytest
import sys
import os
import boto3
from unittest.mock import patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock boto3 for all tests
@pytest.fixture(scope="session", autouse=True)
def mock_boto3_session():
    with patch('boto3.client') as mock:
        yield mock