#!/bin/bash

APP_WORKERS=${APP_WORKERS:-1}

gunicorn --workers "$APP_WORKERS" --preload --worker-class uvicorn.workers.UvicornWorker 'app.app:create_app(config_file="./config/scanners.yml")'
