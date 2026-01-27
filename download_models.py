#!/usr/bin/env python3
"""
Quick model download and cache verification script.
Run this before building Docker to ensure models are available locally.
"""

import os
import sys
from pathlib import Path
from subprocess import run, PIPE

# Required models for the current configuration
REQUIRED_MODELS = [
    # Input Scanners
    "MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
    "protectai/deberta-v3-small-prompt-injection-v2",
    "unitary/unbiased-toxic-roberta",
    
    # Output Scanners
    "vishnun/codenlbert-tiny",
    "madhurjindal/autonlp-Gibberish-Detector-492513457",
    "SamLowe/roberta-base-go_emotions",
    
    # ONNX versions
    "ProtectAI/unbiased-toxic-roberta-onnx",
    "protectai/vishnun-codenlbert-tiny-onnx",
    "SamLowe/roberta-base-go_emotions-onnx",
    
    # Relevance
    "BAAI/bge-small-zh-v1.5",
]


def get_cache_dir():
    """Get HuggingFace cache directory."""
    cache_dir = os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface")
    return Path(cache_dir)


def check_model_cached(model_id: str, cache_dir: Path) -> bool:
    """Check if model is cached locally."""
    model_path = cache_dir / "hub" / model_id.replace("/", "--")
    return model_path.exists()


def download_model(model_id: str) -> bool:
    """Download a model using huggingface-cli."""
    try:
        result = run(
            ["huggingface-cli", "download", model_id, "--resume-download"],
            stdout=PIPE,
            stderr=PIPE,
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: huggingface-cli not found. Install with: pip install huggingface-hub")
        return False


def main():
    """Main verification and download function."""
    cache_dir = get_cache_dir()
    print(f"Cache directory: {cache_dir}\n")

    missing_models = []
    cached_models = []

    print("Checking models...")
    print("-" * 70)

    for model_id in REQUIRED_MODELS:
        if check_model_cached(model_id, cache_dir):
            print(f"✓ {model_id}")
            cached_models.append(model_id)
        else:
            print(f"✗ {model_id} (not cached)")
            missing_models.append(model_id)

    print("-" * 70)
    print(f"Cached: {len(cached_models)}/{len(REQUIRED_MODELS)}")

    if missing_models:
        print(f"\nDownloading {len(missing_models)} missing models...")
        print("-" * 70)

        for model_id in missing_models:
            print(f"Downloading: {model_id}...")
            if download_model(model_id):
                print(f"✓ Downloaded: {model_id}")
            else:
                print(f"✗ Failed to download: {model_id}")
                return 1

    print("-" * 70)
    print("\n✓ All models are ready for offline deployment!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
