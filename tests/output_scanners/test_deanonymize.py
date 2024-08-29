from typing import List, Tuple

import pytest

from llm_guard.input_scanners.anonymize import Anonymize
from llm_guard.output_scanners.deanonymize import Deanonymize, MatchingStrategy
from llm_guard.vault import Vault


@pytest.mark.parametrize(
    "raw_prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "Make an SQL insert statement to add a new user to our database. Name is John Connors. Email is test@test.com "
            "but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
            "the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
            "He works in Test LLC.",
            "Sure! Here's the SQL insert statement to add a new user with the provided information to your database: "
            "INSERT INTO users (Name, Email, Alternate_Email, Phone_Number, IP_Address, Credit_Card_Number, Work_Place)"
            " VALUES ('[REDACTED_PERSON_1]', '[REDACTED_EMAIL_ADDRESS_1]', '[REDACTED_EMAIL_ADDRESS_2]', "
            "'[REDACTED_PHONE_NUMBER_1]', '[REDACTED_IP_ADDRESS_1]', "
            "'[REDACTED_CREDIT_CARD_RE_1]', '[REDACTED_CUSTOM_1]');",
            "Sure! Here's the SQL insert statement to add a new user with the provided information to your database: "
            "INSERT INTO users (Name, Email, Alternate_Email, Phone_Number, IP_Address, Credit_Card_Number, Work_Place)"
            " VALUES ('John Connors', 'test@test.com', 'hello@test.com', '555-123-4567', '192.168.1.100', "
            "'4567-8901-2345-6789', 'Test LLC');",
            True,
            -1.0,
        ),  # Exposed name, email, phone number, credit card number and IP
    ],
)
def test_scan_full(raw_prompt, output, expected_output, expected_valid, expected_score):
    vault = Vault()
    prompt_scanner = Anonymize(vault, hidden_names=["Test LLC"])
    sanitized_prompt, _, _ = prompt_scanner.scan(raw_prompt)

    scanner = Deanonymize(vault, matching_strategy=MatchingStrategy.EXACT)
    sanitized_output, valid, score = scanner.scan(sanitized_prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score


@pytest.mark.parametrize(
    "vault_items,output,expected_output,matching_strategy",
    [
        (
            [
                ("[REDACTED_PERSON_1]", "John Doe"),
                ("[REDACTED_EMAIL_ADDRESS_1]", "test@protectai.com"),
            ],
            "Hello, my name is [REDACTED_PERSON_1] and my email address is [REDACTED_EMAIL_ADDRESS_1].",
            "Hello, my name is John Doe and my email address is test@protectai.com.",
            MatchingStrategy.EXACT.value,
        ),
        (
            [
                ("John Doe", "Kevin Smith"),
            ],
            "Hello, my name is john doe.",
            "Hello, my name is Kevin Smith.",
            MatchingStrategy.CASE_INSENSITIVE.value,
        ),
        (
            [
                ("John Kennedy", "Kevin Smith"),
            ],
            "Hello, my name is John F. Kennedy.",
            "Hello, my name is Kevin Smith.",
            MatchingStrategy.FUZZY.value,
        ),
        (
            [
                ("John Kennedy", "Kevin Smith"),
                ("John Doe", "Doe John"),
            ],
            "Hello, my name is John F. Kennedy and my friend is John Doe.",
            "Hello, my name is Kevin Smith and my friend is Doe John.",
            MatchingStrategy.COMBINED_EXACT_FUZZY.value,
        ),
    ],
)
def test_scan(vault_items: List[Tuple], output: str, expected_output: str, matching_strategy: str):
    vault = Vault(vault_items)
    scanner = Deanonymize(vault, matching_strategy=MatchingStrategy(matching_strategy))
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == expected_output
    assert valid is True
    assert score == -1.0
