import pytest

from llm_guard.input_scanners.anonymize import Anonymize
from llm_guard.output_scanners.deanonymize import Deanonymize
from llm_guard.vault import Vault


@pytest.mark.parametrize(
    "raw_prompt,output,expected_output,expected_valid,expected_score",
    [
        ("", "", "", True, 0.0),  # Empty prompt
        (
            "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com "
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
            " VALUES ('John Doe', 'test@test.com', 'hello@test.com', '555-123-4567', '192.168.1.100', "
            "'4567-8901-2345-6789', 'Test LLC');",
            True,
            0.0,
        ),  # Exposed name, email, phone number, credit card number and IP
    ],
)
def test_scan(raw_prompt, output, expected_output, expected_valid, expected_score):
    vault = Vault()
    prompt_scanner = Anonymize(vault, hidden_names=["Test LLC"])
    sanitized_prompt, _, _ = prompt_scanner.scan(raw_prompt)

    scanner = Deanonymize(vault)
    sanitized_output, valid, score = scanner.scan(sanitized_prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
