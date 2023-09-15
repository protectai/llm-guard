import os
from typing import List

import setuptools
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()


def parse_requirements(file_name: str) -> List[str]:
    with open(file_name) as f:
        return [require.strip() for require in f if require.strip() and not require.startswith("#")]


setuptools.setup(
    name="llm-guard",
    version="0.2.0",
    author="Laiyer.ai",
    author_email="hello@laiyer.ai",
    description=(
        "LLM-Guard is a comprehensive tool designed to fortify the security of Large Language Models (LLMs). By "
        "offering sanitization, detection of harmful language, prevention of data leakage, and resistance against "
        "prompt injection attacks, LLM-Guard ensures that your interactions with LLMs remain safe and "
        "secure."
    ),
    license="MIT",
    keywords="llm, language model, security, adversarial attacks, prompt injection, prompt leakage, PII detection, "
    "self-hardening, firewall",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laiyer-ai/llm-guard",
    package_data={
        "llm_guard": ["**/*.json"],
    },
)
