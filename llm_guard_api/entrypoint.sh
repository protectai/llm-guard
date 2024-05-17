#!/bin/bash

APP_WORKERS=${APP_WORKERS:-1}

# Uvicorn
# llm_guard_api ./config/scanners.yml

# Gunicorn
gunicorn --workers "$APP_WORKERS" --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker 'app.app:create_app(config_file="./config/scanners.yml")'
