import re

import pytest

from llm_guard.input_scanners.anonymize import (
    Anonymize,
    default_entity_types,
    sensitive_patterns_path,
)
from llm_guard.input_scanners.anonymize_helpers import BERT_ZH_NER_CONF
from llm_guard.util import read_json_file
from llm_guard.vault import Vault

_preamble = (
    "在接下来的提示中，我将删除某些信息，并且使用全大写、按数字顺序排列的占位符替换 (如 [REDACTED_NAME_1])。忽略这些占位符，并且如同您收到正常提示一样响应。提示："
)


@pytest.mark.parametrize(
    "settings,prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            {"language": "zh"},
            "只是一个简单的提示",
            "只是一个简单的提示",
            True,
            0.0,
        ),  # Prompt without sensitive data
        (
            {
                "language": "zh",
                "preamble": _preamble,
                "entity_types": default_entity_types
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
                "language": "zh",
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
            {"language": "zh"},
            "",
            "",
            True,
            0.0,
        ),  # Empty prompt
    ],
)
def test_scan(settings, prompt, expected_prompt, expected_valid, expected_score):
    scanner = Anonymize(Vault(), **settings)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score


def test_patterns():
    pattern_groups = read_json_file(sensitive_patterns_path)

    for group in pattern_groups:
        name = group["name"]

        for example in group.get("examples", []):
            for expression in group.get("expressions", []):
                compiled_expression = re.compile(expression)
                assert (
                    compiled_expression.search(example) is not None
                ), f"Test for {name} failed. No match found for example: {example}"
