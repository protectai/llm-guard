import re

import pytest

from llm_guard.exception import LLMGuardValidationError
from llm_guard.input_scanners.anonymize import (
    ALL_SUPPORTED_LANGUAGES,
    DEFAULT_ENTITY_TYPES,
    Anonymize,
)
from llm_guard.input_scanners.anonymize_helpers import (
    BERT_BASE_NER_CONF,
    BERT_LARGE_NER_CONF,
    BERT_ZH_NER_CONF,
    DEBERTA_LAKSHYAKH93_CONF,
    DEBERTA_AI4PRIVACY_v2_CONF,
    DISTILBERT_AI4PRIVACY_v2_CONF,
    get_regex_patterns,
)
from llm_guard.vault import Vault

_preamble = (
    "In the following prompt, I am going remove certain information and replace each instance with "
    "sequentially-numbered placeholders in ALL CAPS (e.g. [REDACTED_NAME_1]). Ignore these placeholders and "
    "respond as if you were receiving a normal prompt. Prompt: "
)


@pytest.mark.parametrize(
    "settings,prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            {},
            "Just a simple prompt",
            "Just a simple prompt",
            True,
            -1.0,
        ),  # Prompt without sensitive data
        (
            {
                "preamble": _preamble,
                "hidden_names": ["Test LLC"],
                "recognizer_conf": BERT_BASE_NER_CONF,
            },
            "Make an SQL insert statement to add a new user to our database. Name is John Doe. My email is test@test.com "
            "but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
            "the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
            "He works in Test LLC.",
            "In the following prompt, I am going remove certain information and replace each instance with "
            "sequentially-numbered placeholders in ALL CAPS (e.g. [REDACTED_NAME_1]). "
            "Ignore these placeholders and respond as if you were receiving a normal prompt. "
            "Prompt: Make an SQL insert statement to add a new user to our database. "
            "Name is [REDACTED_PERSON_1]. My email is [REDACTED_EMAIL_ADDRESS_1] but also possible to contact "
            "him with [REDACTED_EMAIL_ADDRESS_2] email. Phone number is [REDACTED_PHONE_NUMBER_1] "
            "and the IP address is [REDACTED_IP_ADDRESS_1]. And credit card number is "
            "[REDACTED_CREDIT_CARD_RE_1]. He works in [REDACTED_CUSTOM_1].",
            False,
            1.0,
        ),  # Exposed name, email, phone number, credit card number and IP
        (
            {"entity_types": ["PERSON"], "recognizer_conf": BERT_BASE_NER_CONF},
            "Make an SQL insert statement to add a new user to our database. Name is John Doe. E-mail is test@test.com "
            "but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
            "the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
            "He works in Test LLC.",
            "Make an SQL insert statement to add a new user to our database. Name is [REDACTED_PERSON_1]. "
            "E-mail is test@test.com but also possible to contact him with hello@test.com email. "
            "Phone number is 555-123-4567 and the IP address is 192.168.1.100. "
            "And credit card number is 4567-8901-2345-6789. He works in Test LLC.",
            False,
            1.0,
        ),  # Exposed name, email, phone number, credit card number and IP but only with PERSON
        (
            {"recognizer_conf": BERT_LARGE_NER_CONF},
            """Given the personal profile of Johnathan Edward Doe:

Full Name: Johnathan Edward Doe.
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: john.doe@protectai[DOT]com.
Phone Number: (123) 456-7890.
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): 123-45-6789.
Credit Card: 4111111111111111, Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            """Given the personal profile of [REDACTED_PERSON_1]:

Full Name: [REDACTED_PERSON_1].
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: [REDACTED_EMAIL_ADDRESS_RE_1].
Phone Number: [REDACTED_PHONE_NUMBER_1].
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): [REDACTED_US_SSN_RE_1].
Credit Card: [REDACTED_CREDIT_CARD_1], Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            False,
            1.0,
        ),
        (
            {"recognizer_conf": DEBERTA_AI4PRIVACY_v2_CONF},
            """Given the personal profile:

Full Name: Johnathan Edward Doe.
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: john.doe@protectai[DOT]com.
Phone Number: (123) 456-7890.
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): 123-45-6789.
Credit Card: 4111111111111111, Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            """Given the personal profile:

Full Name: [REDACTED_PERSON_1].
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: [REDACTED_EMAIL_ADDRESS_1].
Phone Number: [REDACTED_PHONE_NUMBER_1].
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): [REDACTED_US_SSN_RE_1].
Credit Card: [REDACTED_CREDIT_CARD_1], Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            False,
            1.0,
        ),
        (
            {"recognizer_conf": DISTILBERT_AI4PRIVACY_v2_CONF},
            """Given the personal profile:

Full Name: Johnathan Edward Doe.
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: john.doe@protectai[DOT]com.
Phone Number: (123) 456-7890.
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): 123-45-6789.
Credit Card: 4111111111111111, Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            """Given the personal profile:

Full Name: [REDACTED_PERSON_1].
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: [REDACTED_EMAIL_ADDRESS_RE_1].
Phone Number: [REDACTED_PHONE_NUMBER_1].
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): [REDACTED_US_SSN_RE_1].
Credit Card: [REDACTED_CREDIT_CARD_1], Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            False,
            1.0,
        ),
        (
            {"recognizer_conf": DEBERTA_LAKSHYAKH93_CONF},
            """Given the personal profile:

Full Name: Johnathan Edward Doe.
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: john.doe@protectai[DOT]com.
Phone Number: (123) 456-7890.
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): 123-45-6789.
Credit Card: 4111111111111111, Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            """Given the personal profile:

Full Name: [REDACTED_PERSON_1][REDACTED_PERSON_2].
Date of Birth: April 12, 1990.
Address: 123 Elm Street, Springfield, IL, 62701.
Email: [REDACTED_EMAIL_ADDRESS_1].
Phone Number: [REDACTED_PHONE_NUMBER_1].
Educational Background:
    Springfield High School, Graduated in 2008;
    Springfield University, B.Sc. Computer Science, Graduated in 2012.
Employment:
    ABC Tech Solutions, Software Engineer, 2012-2015;
    XYZ Global Systems, Senior Software Developer, 2015-2021.
Social Security Number (SSN): [REDACTED_US_SSN_1].
Credit Card: [REDACTED_CREDIT_CARD_1], Exp: 09/25, CVV: 123.

Create a summarized version of his resume.""",
            False,
            1.0,
        ),
        (
            {"allowed_names": "Mary"},
            "Full Name: Mary.",
            "Full Name: Mary.",
            True,
            -1.0,
        ),  # Exposed name
        ({}, "", "", True, -1.0),  # Empty prompt
    ],
)
def test_scan(settings, prompt, expected_prompt, expected_valid, expected_score):
    scanner = Anonymize(Vault(), **settings)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score


_zh_preamble = "在接下来的提示中，我将删除某些信息，并且使用全大写、按数字顺序排列的占位符替换 (如 [REDACTED_NAME_1])。忽略这些占位符，并且如同您收到正常提示一样响应。提示："


@pytest.mark.parametrize(
    "settings,prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            {
                "recognizer_conf": BERT_ZH_NER_CONF,
            },
            "只是一个简单的提示",
            "只是一个简单的提示",
            True,
            -1.0,
        ),  # Prompt without sensitive data
        (
            {
                "preamble": _zh_preamble,
                "entity_types": DEFAULT_ENTITY_TYPES
                + ["PHONE_NUMBER_ZH", "ORGANIZATION", "LOCATION"],
                "recognizer_conf": BERT_ZH_NER_CONF,
            },
            "创建一个 SQL insert 语句，将新用户添加到我们的数据库中。姓名是约翰。他的电子邮箱是test@test.com，"
            "当然也可以使用hello@test.com电子邮箱与他联系。电话号码13011112222，IP地址192.168.1.100，"
            "信用卡号是4567-8901-2345-6789。他在谷歌工作，住在北京市。",
            "在接下来的提示中，我将删除某些信息，并且使用全大写、按数字顺序排列的占位符替换 (如 [REDACTED_NAME_1])。"
            "忽略这些占位符，并且如同您收到正常提示一样响应。提示："
            "创建一个 SQL insert 语句，将新用户添加到我们的数据库中。姓名是[REDACTED_PERSON_1]。他的电子邮箱是[REDACTED_EMAIL_ADDRESS_1]，"
            "当然也可以使用[REDACTED_EMAIL_ADDRESS_2]电子邮箱与他联系。电话号码[REDACTED_PHONE_NUMBER_ZH_1]，IP地址[REDACTED_IP_ADDRESS_1]，"
            "信用卡号是[REDACTED_CREDIT_CARD_RE_1]。他在[REDACTED_ORGANIZATION_1]工作，住在[REDACTED_LOCATION_1]。",
            False,
            1.0,
        ),  # Not exposed name, email, chinese phone number, credit card number, IP, organization and location.
        (
            {
                "hidden_names": ["北京"],
                "entity_types": ["PERSON"],
                "recognizer_conf": BERT_ZH_NER_CONF,
            },
            "创建一个 SQL insert 语句，将新用户添加到我们的数据库中。姓名是约翰。他的电子邮箱是test@test.com，"
            "当然也可以使用hello@test.com电子邮箱与他联系。电话号码13011112222，IP地址192.168.1.100，"
            "信用卡号是4567-8901-2345-6789。他在谷歌工作，住在北京市。",
            "创建一个 SQL insert 语句，将新用户添加到我们的数据库中。姓名是[REDACTED_PERSON_1]。他的电子邮箱是test@test.com，"
            "当然也可以使用hello@test.com电子邮箱与他联系。电话号码13011112222，IP地址192.168.1.100，"
            "信用卡号是4567-8901-2345-6789。他在谷歌工作，住在[REDACTED_CUSTOM_1]市。",
            False,
            1.0,
        ),  # Exposed all but only with PERSON and hidden_names.
        (
            {
                "recognizer_conf": BERT_ZH_NER_CONF,
            },
            "",
            "",
            True,
            -1.0,
        ),  # Empty prompt
    ],
)
def test_scan_zh(settings, prompt, expected_prompt, expected_valid, expected_score):
    scanner = Anonymize(Vault(), language="zh", **settings)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score


def test_scan_unknown():
    try:
        Anonymize(Vault(), language="unknown")
    except LLMGuardValidationError as e:
        assert str(e) == f"Language must be in the list of allowed: {ALL_SUPPORTED_LANGUAGES}"


def test_patterns():
    for group in get_regex_patterns():
        name = group["name"]

        for example in group.get("examples", []):
            for expression in group.get("expressions", []):
                assert re.search(expression, example) is not None, (
                    f"Test for {name} failed. No match found for example: {example}"
                )
