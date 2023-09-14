import logging
import time
import traceback
from datetime import timedelta

import pandas as pd
import spacy
import streamlit as st
from output import init_settings as init_output_settings
from output import scan as scan_output
from prompt import init_settings as init_prompt_settings
from prompt import scan as scan_prompt

from llm_guard.vault import Vault

if not spacy.util.is_package("en_core_web_trf"):
    spacy.cli.download("en_core_web_trf")

PROMPT = "prompt"
OUTPUT = "output"
vault = Vault()

st.set_page_config(
    page_title="LLM Guard demo",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "https://laiyer-ai.github.io/llm-guard/",
    },
)

logger = logging.getLogger("llm-guard-demo")
logger.setLevel(logging.INFO)

# Sidebar
st.sidebar.header(
    """
Scanning prompt and output using [LLM Guard](https://laiyer-ai.github.io/llm-guard/)
"""
)

scanner_type = st.sidebar.selectbox("Type", [PROMPT, OUTPUT], index=0)

enabled_scanners = None
settings = None
if scanner_type == PROMPT:
    enabled_scanners, settings = init_prompt_settings()
elif scanner_type == OUTPUT:
    enabled_scanners, settings = init_output_settings()

# Main pannel
with st.expander("About this demo", expanded=False):
    st.info(
        """LLM-Guard is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).
        \n\n[Code](https://github.com/laiyer-ai/llm-guard) |
        [Documentation](https://laiyer-ai.github.io/llm-guard/)"""
    )

    st.markdown(
        "[![Pypi Downloads](https://img.shields.io/pypi/dm/llm-guard.svg)](https://img.shields.io/pypi/dm/llm-guard.svg)"  # noqa
        "[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)"
        "![GitHub Repo stars](https://img.shields.io/github/stars/laiyer-ai/llm-guard?style=social)"
    )

analyzer_load_state = st.info("Starting LLM Guard...")

analyzer_load_state.empty()

# Read default text
with open("prompt_text.txt") as f:
    demo_prompt_text = f.readlines()

with open("output_text.txt") as f:
    demo_output_text = f.readlines()

# Before:
st.subheader("Guard Prompt" if scanner_type == PROMPT else "Guard Output")

if scanner_type == PROMPT:
    st_prompt_text = st.text_area(
        label="Enter prompt", value="".join(demo_prompt_text), height=200, key="prompt_text_input"
    )
elif scanner_type == OUTPUT:
    col1, col2 = st.columns(2)
    st_prompt_text = col1.text_area(
        label="Enter prompt", value="".join(demo_prompt_text), height=300, key="prompt_text_input"
    )

    st_output_text = col2.text_area(
        label="Enter output", value="".join(demo_output_text), height=300, key="output_text_input"
    )

st_result_text = None
st_analysis = None
st_is_valid = None
st_time_delta = None

try:
    with st.form("text_form", clear_on_submit=False):
        submitted = st.form_submit_button("Process")
        if submitted:
            results_valid = {}
            results_score = {}

            start_time = time.monotonic()
            if scanner_type == PROMPT:
                st_result_text, results_valid, results_score = scan_prompt(
                    vault, enabled_scanners, settings, st_prompt_text
                )
            elif scanner_type == OUTPUT:
                st_result_text, results_valid, results_score = scan_output(
                    vault, enabled_scanners, settings, st_prompt_text, st_output_text
                )
            end_time = time.monotonic()
            st_time_delta = timedelta(seconds=end_time - start_time)

            st_is_valid = all(results_valid.values())
            st_analysis = [
                {"scanner": k, "is valid": results_valid[k], "risk score": results_score[k]}
                for k in results_valid
            ]

except Exception as e:
    logger.error(e)
    traceback.print_exc()
    st.error(e)

# After:
if st_is_valid is not None:
    st.subheader(
        f"Results - {'valid' if st_is_valid else 'invalid'} ({st_time_delta.total_seconds()} ms)"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.text_area(label="Sanitized text", value=st_result_text, height=400)

    with col2:
        st.table(pd.DataFrame(st_analysis))
