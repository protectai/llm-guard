import re

import pytest

from llm_guard.input_scanners.anonymize import Anonymize, sensitive_patterns_path
from llm_guard.util import read_json_file
from llm_guard.vault import Vault

_preamble = (
    "In the following prompt, I am going remove certain information and replace each instance with "
    "sequentially-numbered placeholders in ALL CAPS (e.g. [REDACTED_NAME_1]). Ignore these placeholders and "
    "respond as if you were receiving a normal prompt. Prompt: "
)


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid",
    [
        (
            "Just a simple prompt",
            "Just a simple prompt",
            True,
        ),  # Prompt without sensitive data
        (
            "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com "
            "but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
            "the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
            "He works in Test LLC.",
            "In the following prompt, I am going remove certain information and replace each instance with "
            "sequentially-numbered placeholders in ALL CAPS (e.g. [REDACTED_NAME_1]). "
            "Ignore these placeholders and respond as if you were receiving a normal prompt. "
            "Prompt: Make an SQL insert statement to add a new user to our database. "
            "Name is [REDACTED_PERSON_1]. Email is [REDACTED_EMAIL_ADDRESS_1] but also possible to contact "
            "him with [REDACTED_EMAIL_ADDRESS_2] email. Phone number is [REDACTED_PHONE_NUMBER_1] "
            "and the IP address is [REDACTED_IP_ADDRESS_1]. And credit card number is "
            "[REDACTED_CREDIT_CARD_RE_1]. He works in [REDACTED_CUSTOM_1].",
            False,
        ),  # Exposed name, email, phone number, credit card number and IP
        ("", "", True),  # Empty prompt
        ("   ", "   ", True),  # Only whitespace
    ],
)
def test_scan(prompt, expected_prompt, expected_valid):
    scanner = Anonymize(Vault(), preamble=_preamble, hidden_names=["Test LLC"])
    sanitized_prompt, valid = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid


def test_patterns():
    pattern_groups = read_json_file(sensitive_patterns_path)

    for group in pattern_groups:
        name = group["name"]

        found = False
        for example in group["examples"]:
            for expression in group["expressions"]:
                compiled_expression = re.compile(expression)
                if compiled_expression.search(example) is not None:
                    found = True
                    break

            assert found, f"Test for {name} failed. No match found for example: {example}"
