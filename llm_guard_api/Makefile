### --------------------------------------------------------------------------------------------------------------------
### Variables
### --------------------------------------------------------------------------------------------------------------------

# Docker config
DOCKER_IMAGE_NAME=laiyer/llm-guard-api
VERSION=0.3.0

# Other config
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m
ERROR_COLOR=\033[31;01m
WARN_COLOR=\033[33;01m

install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

run:
	DEBUG=true uvicorn src.app:app --reload

build-docker-multi:
	@docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_IMAGE_NAME):$(VERSION) -t $(DOCKER_IMAGE_NAME):latest . --push

run-docker: build-docker
	@docker run -p 8000:8000 -e DEBUG='true' $(DOCKER_IMAGE_NAME):$(VERSION)

.PHONY: install run build-docker run-docker
