# Use the Python 3.11 slim image
FROM python:3.11-slim

# Install system packages needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set up a working directory
WORKDIR $HOME/app

# Copy pyproject.toml and other necessary files for installation
COPY --chown=user:user pyproject.toml ./
COPY --chown=user:user src ./src

# Install the project's dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir ".[cpu]"

RUN python -m spacy download en_core_web_sm

COPY --chown=user:user ./config/scanners.yml ./config/scanners.yml

EXPOSE 8000

CMD ["llm_guard_api", "/home/user/app/config/scanners.yml"]
