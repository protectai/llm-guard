#!/usr/bin/env python3
"""
Model download and verification script for LLM Guard.
Ensures all required models for configured scanners are downloaded and cached.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Model mappings for scanners
SCANNER_MODELS = {
    # Input Scanners
    "BanTopics": {
        "pytorch": ["MoritzLaurer/deberta-v3-base-zeroshot-v2.0"],
        "onnx": ["MoritzLaurer/deberta-v3-base-zeroshot-v2.0"],
    },
    "PromptInjection": {
        "pytorch": ["protectai/deberta-v3-small-prompt-injection-v2"],
        "onnx": ["protectai/deberta-v3-small-prompt-injection-v2"],
    },
    "Toxicity": {
        "pytorch": ["unitary/unbiased-toxic-roberta"],
        "onnx": ["ProtectAI/unbiased-toxic-roberta-onnx"],
    },
    # Output Scanners
    "BanCode": {
        "pytorch": ["vishnun/codenlbert-tiny"],
        "onnx": ["protectai/vishnun-codenlbert-tiny-onnx"],
    },
    "Gibberish": {
        "pytorch": ["madhurjindal/autonlp-Gibberish-Detector-492513457"],
        "onnx": ["madhurjindal/autonlp-Gibberish-Detector-492513457"],
    },
    "EmotionDetection": {
        "pytorch": ["SamLowe/roberta-base-go_emotions"],
        "onnx": ["SamLowe/roberta-base-go_emotions-onnx"],
    },
    "Relevance": {
        "pytorch": ["BAAI/bge-small-zh-v1.5"],
        "onnx": ["BAAI/bge-small-zh-v1.5"],
    },
}


def get_hf_cache_dir() -> Path:
    """Get HuggingFace cache directory."""
    cache_dir = os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface")
    return Path(cache_dir)


def check_model_exists(model_id: str, cache_dir: Path) -> bool:
    """Check if a model is cached locally."""
    # HF cache structure: hub/models--<org>--<model>
    model_path = cache_dir / "hub" / f"models--{model_id.replace('/', '--')}"
    return model_path.exists()


def verify_models(scanners: List[str], use_onnx: bool = True) -> Dict[str, bool]:
    """Verify if all required models are cached."""
    cache_dir = get_hf_cache_dir()
    results = {}
    missing_models = []

    LOGGER.info(f"Checking models in: {cache_dir}")
    LOGGER.info(f"Using ONNX models: {use_onnx}")

    for scanner in scanners:
        if scanner not in SCANNER_MODELS:
            LOGGER.warning(f"Unknown scanner: {scanner}")
            continue

        model_type = "onnx" if use_onnx else "pytorch"
        models = SCANNER_MODELS[scanner].get(model_type, [])

        for model_id in models:
            exists = check_model_exists(model_id, cache_dir)
            results[model_id] = exists

            status = "✓" if exists else "✗"
            LOGGER.info(f"{status} {scanner}: {model_id}")

            if not exists:
                missing_models.append(model_id)

    return results, missing_models


def print_download_command(missing_models: List[str]) -> None:
    """Print huggingface-cli download command for missing models."""
    if not missing_models:
        LOGGER.info("All models are cached!")
        return

    LOGGER.error(f"\nMissing {len(missing_models)} models:")
    LOGGER.error("\nDownload command:")
    cmd = "huggingface-cli download --cache-dir $HF_HOME " + " ".join(missing_models)
    print(cmd)
    print("\nOr download individually:")
    for model in missing_models:
        print(f"huggingface-cli download {model}")


def main():
    """Main verification function."""
    # Scanners used in current config
    scanners = [
        "BanTopics",
        "PromptInjection",
        "Toxicity",
        "BanCode",
        "Gibberish",
        "EmotionDetection",
        "Relevance",
    ]

    use_onnx = True
    results, missing = verify_models(scanners, use_onnx)

    print("\n" + "=" * 70)
    print("MODEL VERIFICATION REPORT")
    print("=" * 70)

    total = len(results)
    cached = sum(1 for v in results.values() if v)
    print(f"Total models: {total}")
    print(f"Cached models: {cached}")
    print(f"Missing models: {len(missing)}")

    if missing:
        print_download_command(missing)
        return 1
    else:
        LOGGER.info("✓ All required models are cached and ready for offline use!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
