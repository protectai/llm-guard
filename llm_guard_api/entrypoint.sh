#!/bin/bash

APP_WORKERS=${APP_WORKERS:-1}
CONFIG_FILE=${CONFIG_FILE:-./config/scanners.yml}

# Enable offline mode for HuggingFace - use only cached models
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

# Uvicorn with workers
uvicorn app.app:create_app --host=0.0.0.0 --port=8000 --workers="$APP_WORKERS" --forwarded-allow-ips="*" --proxy-headers --timeout-keep-alive="2"
