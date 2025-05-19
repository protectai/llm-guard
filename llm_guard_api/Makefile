### --------------------------------------------------------------------------------------------------------------------
### Variables
### --------------------------------------------------------------------------------------------------------------------

# Docker config
DOCKER_IMAGE_NAME=laiyer/llm-guard-api
VERSION=0.3.16

# Other config
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m
ERROR_COLOR=\033[31;01m
WARN_COLOR=\033[33;01m

install:
	@python -m pip install ".[cpu]"

build-docker-multi:
	@docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_IMAGE_NAME):$(VERSION) -t $(DOCKER_IMAGE_NAME):latest . --push

build-docker-cuda-multi:
	@docker buildx build --platform linux/amd64 -t $(DOCKER_IMAGE_NAME):$(VERSION)-cuda -t $(DOCKER_IMAGE_NAME):latest-cuda -f Dockerfile-cuda . --push

run-uvicorn:
	@uvicorn app.app:create_app --host=0.0.0.0 --port=8000 --workers=1 --forwarded-allow-ips="*" --proxy-headers --timeout-keep-alive="2"

run-docker:
	@docker run -p 8000:8000 -e DEBUG='true' -v ./config:/home/user/app/config $(DOCKER_IMAGE_NAME):$(VERSION)

run-docker-cuda:
	@docker run --gpus all -p 8000:8000 -e DEBUG='true' -v ./config:/home/user/app/config $(DOCKER_IMAGE_NAME):$(VERSION)-cuda

.PHONY: install run build-docker-multi build-docker-cuda-multi run-docker run-docker-cuda
