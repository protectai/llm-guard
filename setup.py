import os
import re
from typing import List

import setuptools
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    filepath = "llm_guard/version.py"
    with open(filepath) as version_file:
        (__version__,) = re.findall('__version__ = "(.*)"', version_file.read())
except Exception as error:
    assert False, "Error: Could not open '%s' due %s\n" % (filepath, error)


def parse_requirements(file_name: str) -> List[str]:
    with open(file_name) as f:
        return [require.strip() for require in f if require.strip() and not require.startswith("#")]


TESTS_REQUIRE = parse_requirements("requirements-dev.txt")

EXTRAS_REQUIRE = {
    "onnxruntime": [
        "optimum[onnxruntime]",
    ],
    "onnxruntime-gpu": [
        "optimum[onnxruntime-gpu]",
    ],
    "tests": TESTS_REQUIRE,
}

setuptools.setup(
    name="llm-guard",
    version=__version__,
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
    packages=find_packages(
        include=["llm_guard", "llm_guard.*"],
        exclude=["tests", "tests.*", "llm_guard_api", "llm_guard_api.*"],
    ),
    install_requires=parse_requirements("requirements.txt"),
    extras_require=EXTRAS_REQUIRE,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laiyer-ai/llm-guard",
    package_data={
        "llm_guard": ["**/*.json"],
    },
    python_requires=">=3.9",
)
