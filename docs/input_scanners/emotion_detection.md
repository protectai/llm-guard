# Emotion Detection Scanner

The Emotion Detection Scanner analyzes prompts to detect emotional content using the roberta-base-go_emotions model. It can identify 28 different emotions and can be configured to block specific emotions or detect high-intensity emotional content.

## Attack scenario

This scanner helps prevent emotionally charged or inappropriate prompts that could lead to biased or harmful responses from the LLM. It's particularly useful for:
- Preventing angry or hostile prompts
- Detecting emotionally manipulative content
- Ensuring appropriate emotional tone in user interactions
- Blocking prompts with negative emotions that might influence the model's response

## How it works

The scanner uses the roberta-base-go_emotions model trained on Reddit data to detect 28 different emotions:
- **Positive emotions**: admiration, amusement, approval, caring, excitement, gratitude, joy, love, optimism, pride, relief
- **Negative emotions**: anger, annoyance, confusion, disappointment, disapproval, disgust, embarrassment, fear, grief, nervousness, remorse, sadness
- **Neutral emotions**: curiosity, desire, neutral, realization, surprise

The model outputs probability scores for each emotion, and the scanner flags text when blocked emotions exceed the threshold.

## Usage

```python
from llm_guard.input_scanners import EmotionDetection

# Use default blocked emotions (negative emotions)
scanner = EmotionDetection(threshold=0.5)

# Block specific emotions
scanner = EmotionDetection(
    threshold=0.5,
    blocked_emotions=["anger", "disgust", "fear", "grief"]
)

# Block all emotions above threshold
scanner = EmotionDetection(threshold=0.7)

# Get full emotion analysis
emotion_analysis = scanner.get_emotion_analysis(prompt)

# Scan with full output mode
scanner = EmotionDetection(threshold=0.5, return_full_output=True)
sanitized_prompt, is_valid, risk_score, full_analysis = scanner.scan_with_full_output(prompt)

sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Parameters

- `threshold` (float): Threshold for emotion detection (0.0 to 1.0). Default: 0.5
- `blocked_emotions` (List[str]): List of emotions to block. If None, uses DEFAULT_BLOCKED_EMOTIONS (negative emotions). Default: None
- `match_type` (str): "full" or "sentence" - whether to analyze full text or individual sentences. Default: "full"
- `use_onnx` (bool): Whether to use ONNX for faster inference. Default: False
- `return_full_output` (bool): Whether to return full model output with all emotions and scores. Default: False

## Default Blocked Emotions

By default, the scanner blocks the following negative emotions:
- anger
- annoyance
- disappointment
- disapproval
- disgust
- embarrassment
- fear
- grief
- nervousness
- remorse
- sadness

## Model Information

- **Model**: [SamLowe/roberta-base-go_emotions](https://huggingface.co/SamLowe/roberta-base-go_emotions)
- **ONNX Version**: [SamLowe/roberta-base-go_emotions-onnx](https://huggingface.co/SamLowe/roberta-base-go_emotions-onnx)
- **Model Size**: 125M parameters
- **License**: MIT
- **Training Data**: go_emotions dataset (Reddit data)

## Benchmarks

Environment:
- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:
```sh
python benchmarks/run.py input EmotionDetection
```

## Example

```python
from llm_guard.input_scanners import EmotionDetection

# Create scanner with default settings (blocks negative emotions)
scanner = EmotionDetection(threshold=0.5)

# Test prompts
prompts = [
    "Just a simple question about the weather.",
    "I am so happy to learn about this topic!",
    "I am absolutely furious about this situation!",
    "This makes me feel sad and disappointed."
]

for prompt in prompts:
    sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
    print(f"Prompt: {prompt}")
    print(f"Valid: {is_valid}, Risk Score: {risk_score:.2f}")
    print()
```

Output:
```text
Prompt: Just a simple question about the weather.
Valid: True, Risk Score: 0.00

Prompt: I am so happy to learn about this topic!
Valid: True, Risk Score: 0.00

Prompt: I am absolutely furious about this situation!
Valid: False, Risk Score: 0.85

Prompt: This makes me feel sad and disappointed.
Valid: False, Risk Score: 0.72
```

## Full Emotion Analysis

The scanner also supports full emotion analysis mode that returns all detected emotions with their scores:

```python
from llm_guard.input_scanners import EmotionDetection

# Get full emotion analysis
scanner = EmotionDetection(threshold=0.5)
emotion_analysis = scanner.get_emotion_analysis("I am so happy and excited about this!")
print(emotion_analysis)
# Output: {'joy': 0.85, 'excitement': 0.72, 'optimism': 0.45, ...}

# Scan with full output mode
scanner = EmotionDetection(threshold=0.5, return_full_output=True)
sanitized_prompt, is_valid, risk_score, full_analysis = scanner.scan_with_full_output("I am angry and sad!")
print(f"Valid: {is_valid}, Risk: {risk_score:.2f}")
print(f"Full Analysis: {full_analysis}")
# Output: Valid: False, Risk: 0.75
# Full Analysis: {'anger': 0.82, 'sadness': 0.65, 'disappointment': 0.45, ...}
```
