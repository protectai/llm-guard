# Use the Python 3.12 slim image
FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/protectai/llm-guard
LABEL org.opencontainers.image.description="LLM Guard API"
LABEL org.opencontainers.image.licenses=MIT

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

# Prefetch all HF models used by the configured scanners to bake them into the image.
# Optionally pass HF_TOKEN or HUGGINGFACE_TOKEN at build time for gated models (e.g., prompt injection small).
ARG HF_TOKEN=""
ENV HF_TOKEN=${HF_TOKEN}
RUN set -e; \
    export HF_TOKEN="${HF_TOKEN:-${HUGGINGFACE_TOKEN:-}}"; \
    models="\
Isotonic/deberta-v3-base_finetuned_ai4privacy_v2 \
gyr66/bert-base-chinese-finetuned-ner \
ProtectAI/gyr66-bert-base-chinese-finetuned-ner-onnx \
vishnun/codenlbert-tiny \
protectai/vishnun-codenlbert-tiny-onnx \
guishe/nuner-v1_orgs \
protectai/guishe-nuner-v1_orgs-onnx \
MoritzLaurer/deberta-v3-base-zeroshot-v2.0 \
philomath-1209/programming-language-identification \
madhurjindal/autonlp-Gibberish-Detector-492513457 \
papluca/xlm-roberta-base-language-detection \
ProtectAI/xlm-roberta-base-language-detection-onnx \
protectai/deberta-v3-small-prompt-injection-v2 \
ProtectAI/deberta-v3-small-prompt-injection-v2 \
unitary/unbiased-toxic-roberta \
ProtectAI/unbiased-toxic-roberta-onnx \
SamLowe/roberta-base-go_emotions \
SamLowe/roberta-base-go_emotions-onnx \
valurank/distilroberta-bias \
ProtectAI/distilroberta-bias-onnx \
DunnBC22/codebert-base-Malicious_URLs \
ProtectAI/codebert-base-Malicious_URLs-onnx \
ProtectAI/distilroberta-base-rejection-v1 \
BAAI/bge-small-zh-v1.5"; \
    for repo in $models; do \
        echo "Downloading $repo"; \
        hf download "$repo" --resume-download; \
    done

RUN python -m spacy download zh_core_web_sm

COPY --chown=user:user ./config/scanners.yml ./config/scanners.yml
COPY --chown=user:user entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

ENV PYTHONPATH=$HOME/app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
