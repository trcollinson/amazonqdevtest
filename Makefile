.PHONY: test build deploy local

test:
	pytest tests/

build:
	sam build

deploy:
	sam deploy

local:
	sam local start-api