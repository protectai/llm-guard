### --------------------------------------------------------------------------------------------------------------------
### Variables
### --------------------------------------------------------------------------------------------------------------------

# Docker config
DOCKER_IMAGE_NAME=laiyer/llm-guard-api
VERSION=0.3.12

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

run-uvicorn: install
	llm_guard_api ./config/scanners.yml

run-gunicorn: install
	@gunicorn --workers 1 --preload --worker-class uvicorn.workers.UvicornWorker 'app.app:create_app(config_file="./config/scanners.yml")'

run-docker:
	@docker run -p 8000:8000 -e DEBUG='true' -v ./config:/home/user/app/config $(DOCKER_IMAGE_NAME):$(VERSION)

run-docker-cuda:
	@docker run --gpus all -p 8000:8000 -e DEBUG='true' -v ./config:/home/user/app/config $(DOCKER_IMAGE_NAME):$(VERSION)-cuda

.PHONY: install run build-docker-multi build-docker-cuda-multi run-docker run-docker-cuda
