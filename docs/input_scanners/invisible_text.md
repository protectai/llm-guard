# Invisible Text Scanner

The Invisible Text Scanner is designed to detect and remove non-printable, invisible Unicode characters from text inputs.
This is crucial for maintaining text integrity in Large Language Models (LLMs) and safeguarding against steganography-based attacks.

## Attack Scenario

Steganography via invisible text can occur in various online contexts, such as Amazon reviews, emails, websites, or even security logs.
This modern form of prompt injection is less detectable than traditional methods like "white on white" text, making it a versatile tool for hidden communications or instructions.

For instance, it can be in the payload copied from a website and impact analysis done in the LLM chat.

## How it works

The scanner targets invisible Unicode characters, particularly in the Private Use Areas (PUA) of Unicode, which include:

- **Basic Multilingual Plane**: U+E000 to U+F8FF
- **Supplementary Private Use Area-A**: U+F0000 to U+FFFFD
- **Supplementary Private Use Area-B**: U+100000 to U+10FFFD

These characters, while valid in Unicode, are not rendered by most fonts but can be checked [here](https://www.soscisurvey.de/tools/view-chars.php).

It detects and removes characters in categories 'Cf' (Format characters), 'Cc' (Control characters), 'Co' (Private use characters), and 'Cn' (Unassigned characters), which are typically non-printable.

Here is the Python code to convert a string to a string of Private Use Area characters (from this [Tweet](https://twitter.com/rez0__/status/1745545813512663203)):

```python
import pyperclip
def convert_to_tag_chars(input_string):
 return ''.join(chr(0xE0000 + ord(ch)) for ch in input_string)

# Example usage:
user_input = input("Enter a string to convert to tag characters: ")
tagged_output = convert_to_tag_chars(user_input)
print("Tagged output:", tagged_output)
pyperclip.copy(tagged_output)
```

## Usage

```python
from llm_guard.input_scanners import InvisibleText

scanner = InvisibleText()
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Benchmarks

Run the following script:

```sh
python benchmarks/run.py input InvisibleText
```

This scanner uses built-in functions, which makes it fast.
