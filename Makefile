.PHONY: test test-cov build deploy local

test:
	pytest tests/

test-cov:
	pytest --cov=hello_world --cov-report=term --cov-report=html tests/

build:
	sam build

deploy:
	sam deploy

local:
	sam local start-api