.PHONY: test test-cov build deploy local install-requirements

test:
	pytest tests/

test-cov:
	pytest --cov=hello_world --cov=users --cov=website_to_text --cov-report=term --cov-report=html tests/

build:
	sam build

deploy:
	sam deploy

local:
	sam local start-api

install-requirements:
	@echo "Installing all requirements.txt files in the project..."
	@find . -name "requirements.txt" -type f -not -path "*/\.*" -exec pip install -r {} \;