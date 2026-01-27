#!/bin/bash
# Build script with model download and verification for offline deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}LLM Guard API - Offline Build Script${NC}"
echo -e "${YELLOW}========================================${NC}"

# Check if HF token is provided
if [ -z "$HF_TOKEN" ]; then
    echo -e "${RED}Error: HF_TOKEN environment variable is not set${NC}"
    echo "Please set your HuggingFace token:"
    echo "  export HF_TOKEN=your_hf_token_here"
    exit 1
fi

DOCKER_IMAGE="${DOCKER_IMAGE:-llm-guard-api:latest}"
DOCKERFILE="${DOCKERFILE:-./llm_guard_api/Dockerfile}"

echo -e "${GREEN}Building with HuggingFace token${NC}"
echo -e "${GREEN}Image: $DOCKER_IMAGE${NC}"
echo -e "${GREEN}Dockerfile: $DOCKERFILE${NC}"

# Build Docker image with model downloads and verification
docker build \
    --secret HF_TOKEN="$HF_TOKEN" \
    -f "$DOCKERFILE" \
    -t "$DOCKER_IMAGE" \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}Image: $DOCKER_IMAGE${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "The Docker image now contains:"
    echo "  • All required HuggingFace models cached locally"
    echo "  • Offline mode enabled for HuggingFace"
    echo "  • No internet access required at runtime"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 8000:8000 $DOCKER_IMAGE"
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
