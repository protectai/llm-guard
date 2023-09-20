import pytest

from llm_guard.input_scanners.secrets import Secrets


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            "Just a simple prompt",
            "Just a simple prompt",
            True,
            0.0,
        ),  # Prompt without sensitive data
        (
            'I need to pass a key\naws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"',  # gitleaks:allow
            'I need to pass a key\naws_secret_access_key="************"',
            False,
            1.0,
        ),  # Prompt with key
        (
            "My github token is: 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",  # gitleaks:allow
            "My github token is: ******",
            False,
            1.0,
        ),  # Prompt with Github token
        (
            "My JWT token is: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # gitleaks:allow
            "My JWT token is: ******SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            False,
            1.0,
        ),  # Prompt with a JWT token
        (
            "Use this URL: https://username:password@llm-guard.com",
            "Use this URL: https://username:******@llm-guard.com",
            False,
            1.0,
        ),  # Prompt with HTTP basic auth
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Secrets()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
