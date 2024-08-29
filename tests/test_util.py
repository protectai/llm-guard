import pytest

from llm_guard.util import (
    calculate_risk_score,
    chunk_text,
    extract_urls,
    remove_markdown,
    split_text_by_sentences,
    split_text_to_word_chunks,
    truncate_tokens_head_tail,
)


@pytest.mark.parametrize(
    "score, threshold, expected_risk_score",
    [
        (0.2, 0.5, -0.6),
        (0.4, 0.5, -0.2),
        (0.6, 0.5, 0.2),
        (0.8, 0.5, 0.6),
    ],
)
def test_calculate_risk_score_calculates_correctly(score, threshold, expected_risk_score):
    risk_score = calculate_risk_score(score, threshold)
    assert risk_score == expected_risk_score


@pytest.mark.parametrize(
    "text, chunk_size, expected_chunks",
    [
        ("This is a test.", 4, ["This", " is ", "a te", "st."]),
        ("Short", 10, ["Short"]),
    ],
)
def test_chunk_text_chunks_correctly(text, chunk_size, expected_chunks):
    chunks = chunk_text(text, chunk_size)
    assert chunks == expected_chunks


@pytest.mark.parametrize(
    "text, expected_sentences",
    [
        ("This is a test. Another sentence.", ["This is a test.", "Another sentence."]),
        ("Single sentence", ["Single sentence"]),
    ],
)
def test_split_text_by_sentences_splits_correctly(text, expected_sentences):
    sentences = split_text_by_sentences(text)
    assert sentences == expected_sentences


@pytest.mark.parametrize(
    "input_length, chunk_length, overlap_length, expected_chunks",
    [
        (100, 50, 10, [(0, 50), (40, 90), (80, 100)]),
        (30, 50, 10, [(0, 30)]),
    ],
)
def test_split_text_to_word_chunks_splits_correctly(
    input_length, chunk_length, overlap_length, expected_chunks
):
    chunks = split_text_to_word_chunks(input_length, chunk_length, overlap_length)
    assert chunks == expected_chunks


@pytest.mark.parametrize(
    "tokens, max_length, head_length, tail_length, expected_tokens",
    [
        (list(range(600)), 512, 128, 382, list(range(128)) + list(range(218, 600))),
        (list(range(400)), 512, 128, 382, list(range(400))),
    ],
)
def test_truncate_tokens_head_tail_truncates_correctly(
    tokens, max_length, head_length, tail_length, expected_tokens
):
    truncated_tokens = truncate_tokens_head_tail(tokens, max_length, head_length, tail_length)
    assert truncated_tokens == expected_tokens


@pytest.mark.parametrize(
    "text, expected_urls",
    [
        ("Check this link: http://example.com", ["http://example.com"]),
        ("No URLs here", []),
    ],
)
def test_extract_urls_extracts_correctly(text, expected_urls):
    urls = extract_urls(text)
    assert urls == expected_urls


@pytest.mark.parametrize(
    "text, expected_clean_text",
    [
        (
            "**bold** *italic* [link](http://example.com) and some text",
            "bold italic  and some text",
        ),
        ("# Header\n> Blockquote\n`code`", "Header\n Blockquote"),
    ],
)
def test_remove_markdown_removes_correctly(text, expected_clean_text):
    clean_text = remove_markdown(text)
    assert clean_text == expected_clean_text
