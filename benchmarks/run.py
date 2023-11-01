import argparse
import json
import timeit
from functools import lru_cache
from typing import Dict, List

import numpy

from llm_guard import input_scanners, output_scanners
from llm_guard.input_scanners.anonymize_helpers.analyzer import RECOGNIZER_SPACY_EN_PII_FAST
from llm_guard.input_scanners.base import Scanner as InputScanner
from llm_guard.output_scanners.base import Scanner as OutputScanner
from llm_guard.output_scanners.relevance import MODEL_EN_BGE_SMALL
from llm_guard.vault import Vault

vault = Vault()


def build_input_scanner(scanner_name: str) -> InputScanner:
    if scanner_name == "Anonymize":
        return input_scanners.Anonymize(vault=vault, recognizer=RECOGNIZER_SPACY_EN_PII_FAST)

    if scanner_name == "BanSubstrings":
        return input_scanners.BanSubstrings(
            substrings=["backdoor", "malware", "virus"], match_type="word"
        )

    if scanner_name == "BanTopics":
        return input_scanners.BanTopics(topics=["violence", "attack", "war"])

    if scanner_name == "Code":
        return input_scanners.Code(denied=["java"])

    if scanner_name == "Language":
        return input_scanners.Language(valid_languages=["en", "es"])

    if scanner_name == "PromptInjection":
        return input_scanners.PromptInjection()

    if scanner_name == "Regex":
        return input_scanners.Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"])

    if scanner_name == "Secrets":
        return input_scanners.Secrets()

    if scanner_name == "Sentiment":
        return input_scanners.Sentiment()

    if scanner_name == "TokenLimit":
        return input_scanners.TokenLimit(limit=50)

    if scanner_name == "Toxicity":
        return input_scanners.Toxicity()

    raise ValueError("Scanner not found")


def build_output_scanner(scanner_name: str) -> OutputScanner:
    if scanner_name == "BanSubstrings":
        return output_scanners.BanSubstrings(
            substrings=["backdoor", "malware", "virus"], match_type="word"
        )

    if scanner_name == "BanTopics":
        return output_scanners.BanTopics(topics=["violence", "attack", "war"])

    if scanner_name == "Bias":
        return output_scanners.Bias()

    if scanner_name == "Code":
        return output_scanners.Code(denied=["java"])

    if scanner_name == "Deanonymize":
        return output_scanners.Deanonymize(vault)

    if scanner_name == "JSON":
        return output_scanners.JSON()

    if scanner_name == "Language":
        return output_scanners.Language(valid_languages=["en", "es"])

    if scanner_name == "LanguageSame":
        return output_scanners.LanguageSame()

    if scanner_name == "MaliciousURLs":
        return output_scanners.MaliciousURLs()

    if scanner_name == "NoRefusal":
        return output_scanners.NoRefusal()

    if scanner_name == "Refutation":
        return output_scanners.Refutation()

    if scanner_name == "Regex":
        return output_scanners.Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"])

    if scanner_name == "Relevance":
        return output_scanners.Relevance(model=MODEL_EN_BGE_SMALL)

    if scanner_name == "Sensitive":
        return output_scanners.Sensitive(recognizer=RECOGNIZER_SPACY_EN_PII_FAST, redact=True)

    if scanner_name == "Sentiment":
        return output_scanners.Sentiment()

    if scanner_name == "Toxicity":
        return output_scanners.Toxicity()

    raise ValueError("Scanner not found")


@lru_cache(maxsize=None)
def get_input_test_data() -> Dict:
    with open("input_examples.json", "r") as file:
        return json.load(file)


@lru_cache(maxsize=None)
def get_output_test_data() -> (str, str):
    with open("output_examples.json", "r") as file:
        data = json.load(file)

    return {key: tuple(value) for key, value in data.items()}


def benchmark_input_scanner(scanner_name: str, repeat_times: int = 5) -> (List, int):
    scanner = build_input_scanner(scanner_name)

    prompt = get_input_test_data()[scanner_name]

    latency_list = timeit.repeat(lambda: scanner.scan(prompt), number=1, repeat=repeat_times)

    return latency_list, len(prompt)


def benchmark_output_scanner(scanner_name: str, repeat_times: int = 5) -> (List, int):
    scanner = build_output_scanner(scanner_name)

    prompt, output = get_output_test_data()[scanner_name]

    latency_list = timeit.repeat(
        lambda: scanner.scan(prompt, output), number=1, repeat=repeat_times
    )

    return latency_list, len(output)


def get_output(scanner_name: str, scanner_type: str, latency_list, input_length: int) -> Dict:
    latency_ms = sum(latency_list) / float(len(latency_list)) * 1000.0
    latency_variance = numpy.var(latency_list, dtype=numpy.float64) * 1000.0
    throughput = input_length * (1000.0 / latency_ms)

    return {
        "scanner": scanner_name,
        "scanner Type": scanner_type,
        "input_length": input_length,
        "test_times": len(latency_list),
        "latency_variance": f"{latency_variance:.2f}",
        "latency_90_percentile": f"{numpy.percentile(latency_list, 90) * 1000.0:.2f}",
        "latency_95_percentile": f"{numpy.percentile(latency_list, 95) * 1000.0:.2f}",
        "latency_99_percentile": f"{numpy.percentile(latency_list, 99) * 1000.0:.2f}",
        "average_latency_ms": f"{latency_ms:.2f}",
        "QPS": f"{throughput:.2f}",
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark scanners in llm-guard library.")
    parser.add_argument(
        "type", choices=["input", "output"], help="Type of the scanner to benchmark."
    )
    parser.add_argument("scanner", type=str, help="Name of the scanner class to benchmark.")

    args = parser.parse_args()

    if args.type == "input":
        latency_list, length = benchmark_input_scanner(args.scanner)
    elif args.type == "output":
        latency_list, length = benchmark_output_scanner(args.scanner)
    else:
        raise ValueError("Type is not found")

    # Structured Output
    output = get_output(args.scanner, args.type, latency_list, length)
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    main()
