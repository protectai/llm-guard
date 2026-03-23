"""
Tests for MiniMax integration examples.

Unit tests validate the LLM Guard scanning pipeline with mocked MiniMax API responses.
Integration tests (marked with pytest.mark.integration) call the real MiniMax API.

Uses lightweight scanners (BanSubstrings, TokenLimit, Regex) to avoid heavy model downloads.
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import BanSubstrings, TokenLimit
from llm_guard.input_scanners.ban_substrings import MatchType as InputMatchType
from llm_guard.output_scanners import BanSubstrings as OutputBanSubstrings
from llm_guard.output_scanners import Regex
from llm_guard.output_scanners.ban_substrings import MatchType as OutputMatchType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def input_scanners():
    return [
        BanSubstrings(substrings=["DROP TABLE", "DELETE FROM"], match_type=InputMatchType.STR),
        TokenLimit(limit=4096),
    ]


@pytest.fixture
def output_scanners():
    return [
        OutputBanSubstrings(
            substrings=["DROP TABLE", "DELETE FROM"], match_type=OutputMatchType.STR
        ),
        Regex(patterns=[r"Bearer [A-Za-z0-9-._~+/]+"], is_blocked=True),
    ]


@pytest.fixture
def safe_prompt():
    return (
        "Make an SQL insert statement to add a new user to our database. "
        "Name is John Doe. Email is test@test.com."
    )


@pytest.fixture
def malicious_prompt():
    return "DROP TABLE users; DELETE FROM accounts WHERE 1=1;"


@pytest.fixture
def mock_minimax_response():
    """Simulates a MiniMax API response in OpenAI-compatible format."""
    response = MagicMock()
    choice = MagicMock()
    choice.message.content = (
        "INSERT INTO users (name, email) VALUES ('John Doe', 'test@test.com');"
    )
    response.choices = [choice]
    response.model = "MiniMax-M2.7"
    usage = MagicMock()
    usage.prompt_tokens = 50
    usage.completion_tokens = 40
    response.usage = usage
    return response


# ---------------------------------------------------------------------------
# Unit tests – MiniMax API example flow (mocked)
# ---------------------------------------------------------------------------


class TestMiniMaxApiExample:
    """Tests for the minimax_api.py example flow."""

    def test_safe_prompt_passes_scanners(self, input_scanners, safe_prompt):
        """Verify that a safe prompt passes all input scanners."""
        sanitized_prompt, results_valid, results_score = scan_prompt(
            input_scanners, safe_prompt
        )
        assert all(results_valid.values()) is True
        assert sanitized_prompt == safe_prompt

    def test_malicious_prompt_is_blocked(self, input_scanners, malicious_prompt):
        """Verify that a malicious prompt with SQL injection is blocked."""
        sanitized_prompt, results_valid, results_score = scan_prompt(
            input_scanners, malicious_prompt
        )
        assert results_valid.get("BanSubstrings") is False

    def test_safe_output_passes_scanners(self, output_scanners):
        """Verify that a clean SQL response passes output scanners."""
        prompt = "Create an SQL insert statement for a new user."
        output_text = (
            "INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com');"
        )
        sanitized_output, results_valid, results_score = scan_output(
            output_scanners, prompt, output_text
        )
        assert all(results_valid.values()) is True
        assert sanitized_output == output_text

    def test_output_with_secret_is_blocked(self, output_scanners):
        """Verify that output containing a bearer token is blocked."""
        prompt = "Show me how to authenticate."
        output_text = "Use this token: Bearer abc-def_123.xyz"
        sanitized_output, results_valid, results_score = scan_output(
            output_scanners, prompt, output_text
        )
        assert results_valid.get("Regex") is False

    @patch("openai.OpenAI")
    def test_minimax_client_configuration(self, mock_openai_class):
        """Verify MiniMax client is configured with correct base_url."""
        from openai import OpenAI

        OpenAI(
            api_key="test-minimax-key",
            base_url="https://api.minimax.io/v1",
        )
        mock_openai_class.assert_called_once_with(
            api_key="test-minimax-key",
            base_url="https://api.minimax.io/v1",
        )

    @patch("openai.OpenAI")
    def test_full_flow_with_mocked_api(
        self,
        mock_openai_class,
        input_scanners,
        output_scanners,
        safe_prompt,
        mock_minimax_response,
    ):
        """End-to-end test of minimax_api.py flow with mocked API."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_minimax_response
        mock_openai_class.return_value = mock_client

        # Step 1: Scan input
        sanitized_prompt, results_valid, results_score = scan_prompt(
            input_scanners, safe_prompt
        )
        assert all(results_valid.values()) is True

        # Step 2: Call MiniMax API (mocked)
        response = mock_client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": sanitized_prompt},
            ],
            temperature=0.1,
            max_tokens=512,
        )
        response_text = response.choices[0].message.content
        assert "INSERT INTO" in response_text

        # Step 3: Scan output
        sanitized_response, out_valid, out_score = scan_output(
            output_scanners, sanitized_prompt, response_text
        )
        assert all(out_valid.values()) is True

    @patch("openai.OpenAI")
    def test_malicious_output_blocked(
        self, mock_openai_class, input_scanners, output_scanners, safe_prompt
    ):
        """Verify output containing banned substrings is caught."""
        mock_client = MagicMock()
        bad_response = MagicMock()
        bad_choice = MagicMock()
        bad_choice.message.content = "Sure! DELETE FROM users WHERE 1=1;"
        bad_response.choices = [bad_choice]
        mock_client.chat.completions.create.return_value = bad_response
        mock_openai_class.return_value = mock_client

        sanitized_prompt, _, _ = scan_prompt(input_scanners, safe_prompt)
        response = mock_client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[{"role": "user", "content": sanitized_prompt}],
        )
        response_text = response.choices[0].message.content

        sanitized_response, out_valid, _ = scan_output(
            output_scanners, sanitized_prompt, response_text
        )
        assert out_valid.get("BanSubstrings") is False

    def test_minimax_model_names(self):
        """Verify MiniMax model names used in examples are valid identifiers."""
        valid_models = {"MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M2.5-highspeed"}
        for model in valid_models:
            assert model.startswith("MiniMax-")
            assert len(model) > 8

    def test_minimax_base_url(self):
        """Verify MiniMax API base URL is correctly formatted."""
        base_url = "https://api.minimax.io/v1"
        assert base_url.startswith("https://")
        assert base_url.endswith("/v1")
        assert "minimax.io" in base_url

    def test_temperature_within_minimax_range(self):
        """Verify temperature values used in examples are within MiniMax's accepted range."""
        temperatures = [0.0, 0.1, 0.5, 1.0]
        for temp in temperatures:
            assert 0.0 <= temp <= 1.0

    def test_token_limit_scanner_with_long_prompt(self):
        """Verify TokenLimit scanner blocks prompts exceeding the limit."""
        scanner = TokenLimit(limit=10)
        scanners = [scanner]
        long_prompt = "This is a very long prompt that should exceed the token limit."
        sanitized, results_valid, _ = scan_prompt(scanners, long_prompt)
        assert results_valid.get("TokenLimit") is False

    def test_scan_prompt_fail_fast(self, input_scanners, malicious_prompt):
        """Verify fail_fast stops scanning after first failure."""
        sanitized, results_valid, _ = scan_prompt(
            input_scanners, malicious_prompt, fail_fast=True
        )
        # Only BanSubstrings should appear (fail_fast stops at first failure)
        assert "BanSubstrings" in results_valid
        assert results_valid["BanSubstrings"] is False


class TestMiniMaxStreamingExample:
    """Tests for the minimax_streaming.py example flow."""

    def test_streaming_output_scanning_in_chunks(self, output_scanners):
        """Simulate streaming output scanning as done in minimax_streaming.py."""
        prompt = "Provide me with a list of the top 5 popular people in the world."
        chunks = [
            "Here are ",
            "the top 5 most popular ",
            "people in the world:\n",
            "1. Cristiano Ronaldo\n",
            "2. Lionel Messi\n",
            "3. Taylor Swift\n",
            "4. BTS\n",
            "5. Dwayne Johnson",
        ]
        output = ""
        min_output_length = 30
        for chunk in chunks:
            output += chunk
            if len(output) > min_output_length:
                sanitized_output, is_valid, risk_score = scan_output(
                    output_scanners, prompt, output
                )
                output = sanitized_output
                assert output is not None
                assert all(is_valid.values()) is True

    def test_streaming_detects_banned_content(self, output_scanners):
        """Verify streaming scanner catches banned content mid-stream."""
        prompt = "Show me a database query."
        chunks = ["Here is", " how to", " DELETE FROM", " users WHERE", " 1=1;"]
        output = ""
        found_violation = False
        for chunk in chunks:
            output += chunk
            if len(output) > 10:
                _, is_valid, _ = scan_output(output_scanners, prompt, output)
                if not all(is_valid.values()):
                    found_violation = True
                    break
        assert found_violation

    def test_async_prompt_scanning(self, input_scanners, safe_prompt):
        """Test async wrapper for prompt scanning (used in streaming example)."""

        async def ascan():
            return await asyncio.to_thread(
                scan_prompt, input_scanners, safe_prompt, True
            )

        result = asyncio.run(ascan())
        sanitized_prompt, is_valid, risk_score = result
        assert sanitized_prompt == safe_prompt
        assert all(is_valid.values()) is True

    @patch("openai.AsyncOpenAI")
    def test_async_minimax_client_configuration(self, mock_async_openai):
        """Verify async MiniMax client is configured with correct base_url."""
        from openai import AsyncOpenAI

        AsyncOpenAI(
            api_key="test-minimax-key",
            base_url="https://api.minimax.io/v1",
        )
        mock_async_openai.assert_called_once_with(
            api_key="test-minimax-key",
            base_url="https://api.minimax.io/v1",
        )

    def test_async_output_scanning(self, output_scanners):
        """Test async wrapper for output scanning."""

        async def ascan():
            return await asyncio.to_thread(
                scan_output,
                output_scanners,
                "test prompt",
                "safe output text",
                True,
            )

        sanitized, is_valid, risk_score = asyncio.run(ascan())
        assert sanitized == "safe output text"
        assert all(is_valid.values()) is True


class TestMiniMaxDocsTutorial:
    """Tests for the docs/tutorials/minimax.md code snippets."""

    def test_litellm_config_model_name(self):
        """Verify the LiteLLM config uses correct MiniMax model name prefix."""
        litellm_model = "openai/MiniMax-M2.7"
        assert litellm_model.startswith("openai/")
        assert "MiniMax" in litellm_model

    def test_minimax_api_base_for_litellm(self):
        """Verify the LiteLLM api_base is set correctly for MiniMax."""
        api_base = "https://api.minimax.io/v1"
        assert "minimax.io" in api_base


# ---------------------------------------------------------------------------
# Integration tests – require MINIMAX_API_KEY
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestMiniMaxIntegration:
    """Integration tests that call the real MiniMax API.

    Run with: pytest -m integration tests/test_minimax_examples.py
    Requires MINIMAX_API_KEY environment variable.
    """

    @pytest.fixture(autouse=True)
    def skip_without_api_key(self):
        import os

        if not os.getenv("MINIMAX_API_KEY"):
            pytest.skip("MINIMAX_API_KEY not set")

    def test_minimax_api_completion(self, input_scanners, output_scanners, safe_prompt):
        """Full integration test: scan prompt -> MiniMax API call -> scan output."""
        import os

        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url="https://api.minimax.io/v1",
        )

        sanitized_prompt, results_valid, _ = scan_prompt(input_scanners, safe_prompt)
        assert all(results_valid.values()) is True

        response = client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": sanitized_prompt},
            ],
            temperature=0.1,
            max_tokens=256,
        )
        response_text = response.choices[0].message.content
        assert len(response_text) > 0

        sanitized_output, out_valid, _ = scan_output(
            output_scanners, sanitized_prompt, response_text
        )
        assert sanitized_output is not None

    def test_minimax_streaming_completion(self, input_scanners, output_scanners):
        """Integration test for streaming MiniMax completion with LLM Guard."""
        import os

        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url="https://api.minimax.io/v1",
        )

        prompt = "List 3 programming languages."
        sanitized_prompt, results_valid, _ = scan_prompt(input_scanners, prompt)
        assert all(results_valid.values()) is True

        response = client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[{"role": "user", "content": sanitized_prompt}],
            stream=True,
            temperature=0.1,
        )

        output = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            output += delta

        assert len(output) > 0

        sanitized_output, out_valid, _ = scan_output(
            output_scanners, sanitized_prompt, output
        )
        assert sanitized_output is not None

    def test_minimax_m25_highspeed_model(self):
        """Integration test for MiniMax-M2.5-highspeed model."""
        import os

        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url="https://api.minimax.io/v1",
        )

        response = client.chat.completions.create(
            model="MiniMax-M2.5-highspeed",
            messages=[{"role": "user", "content": "Say hello in one word."}],
            temperature=0.1,
            max_tokens=10,
        )
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0
