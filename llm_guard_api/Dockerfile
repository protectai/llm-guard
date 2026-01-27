# Use the Python 3.12 slim image
FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/protectai/llm-guard
LABEL org.opencontainers.image.description="LLM Guard API - Offline Deployment"
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.title="LLM Guard API Offline"

# This Dockerfile builds a self-contained image with:
# - All required HuggingFace models pre-downloaded and cached
# - Offline mode enabled for HuggingFace
# - No internet access required at runtime

# Install system packages needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Set up a working directory
WORKDIR $HOME/app

# Copy pyproject.toml and other necessary files for installation
COPY --chown=user:user pyproject.toml ./
COPY --chown=user:user app ./app

# Install the project's dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[cpu]"



# Copy verification script
COPY --chown=user:user verify_models.py ./

# Prefetch all HF models used by the configured scanners to bake them into the image.
RUN --mount=type=secret,id=HF_TOKEN,env=HF_TOKEN \
    set -e; \
    huggingface-cli login --token $HF_TOKEN && \
    models="\
MoritzLaurer/deberta-v3-base-zeroshot-v2.0 \
protectai/deberta-v3-small-prompt-injection-v2 \
unitary/unbiased-toxic-roberta \
ProtectAI/unbiased-toxic-roberta-onnx \
vishnun/codenlbert-tiny \
protectai/vishnun-codenlbert-tiny-onnx \
madhurjindal/autonlp-Gibberish-Detector-492513457 \
SamLowe/roberta-base-go_emotions \
SamLowe/roberta-base-go_emotions-onnx \
BAAI/bge-small-zh-v1.5"; \
    for repo in $models; do \
        echo "Downloading $repo"; \
        huggingface-cli download "$repo" --resume-download || true; \
    done && \
    echo "Verifying model downloads..." && \
    python verify_models.py || exit 1

RUN python -m spacy download zh_core_web_sm

COPY --chown=user:user ./config/scanners.yml ./config/scanners.yml
COPY --chown=user:user entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

ENV PYTHONPATH=$HOME/app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
