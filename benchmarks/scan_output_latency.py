import pytest

from llm_guard import scan_output
from llm_guard.output_scanners import (
    BanSubstrings,
    BanTopics,
    Bias,
    Code,
    Deanonymize,
    MaliciousURLs,
    NoRefusal,
    Refutation,
    Regex,
    Relevance,
    Sensitive,
    Sentiment,
    Toxicity,
)
from llm_guard.vault import Vault

vault = Vault()

test_prompt = "Make an SQL insert statement to add a new user to our db (). Name is John Doe. Email is test@test.com "
"but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and the IP "
"address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. He works in Test LLC."

outputs = [
    # Data leakage
    "INSERT INTO users (Name, Email, Alternate_Email, Phone_Number, IP_Address, Credit_Card_Number, Work_Place)"
    " VALUES ('John Doe', 'test@test.com', 'hello@test.com', '555-123-4567', '192.168.1.100', "
    "'4567-8901-2345-6789', 'Test LLC');"
]

# Just data leakage scanners
basic_scanners = [Deanonymize(vault), Sensitive()]


@pytest.mark.parametrize("output", outputs)
def test_scan_prompt_basic(benchmark, output: str):
    _ = benchmark.pedantic(
        scan_output,
        kwargs={"scanners": basic_scanners, "prompt": test_prompt, "output": output},
        iterations=1,
        rounds=1,
    )


# Data leakage, bias and toxicity scanners
intermediate_scanners = [Deanonymize(vault), Sensitive(), Bias(), Toxicity()]


@pytest.mark.parametrize("output", outputs)
def test_scan_prompt_intermediate(benchmark, output: str):
    _ = benchmark.pedantic(
        scan_output,
        kwargs={"scanners": intermediate_scanners, "prompt": test_prompt, "output": output},
        iterations=1,
        rounds=1,
    )


# All scanners
advanced_scanners = [
    BanSubstrings(substrings=["ACME CORP"], match_type="word"),
    BanTopics(topics=["facebook"]),
    Bias(),
    Code(denied=["java"]),
    Deanonymize(vault),
    MaliciousURLs(),
    NoRefusal(),
    Refutation(),
    Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"]),
    Relevance(),
    Sensitive(),
    Sentiment(),
    Toxicity(),
]


@pytest.mark.parametrize("output", outputs)
def test_scan_prompt_advanced(benchmark, output: str):
    _ = benchmark.pedantic(
        scan_output,
        kwargs={"scanners": advanced_scanners, "prompt": test_prompt, "output": output},
        iterations=5,
        rounds=5,
    )
