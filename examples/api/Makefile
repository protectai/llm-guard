### --------------------------------------------------------------------------------------------------------------------
### Variables
### --------------------------------------------------------------------------------------------------------------------

# Docker config
DOCKER_IMAGE_NAME=llm-guard-api
DOCKER_HUB_USERNAME=laiyer
VERSION=latest

# Other config
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m
ERROR_COLOR=\033[31;01m
WARN_COLOR=\033[33;01m

install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

run:
	DEBUG=true uvicorn app:app --reload

build-docker:
	@docker build -t $(DOCKER_IMAGE_NAME):$(VERSION) .

run-docker: build-docker
	@docker run -p 8000:8000 -e DEBUG='true' $(DOCKER_IMAGE_NAME):$(VERSION)

tag-docker:
	@docker tag $(DOCKER_IMAGE_NAME):$(VERSION) $(DOCKER_HUB_USERNAME)/$(DOCKER_IMAGE_NAME):$(VERSION)

push-docker: tag-docker
	@docker push $(DOCKER_HUB_USERNAME)/$(DOCKER_IMAGE_NAME):$(VERSION)

.PHONY: install run build-docker run-docker
