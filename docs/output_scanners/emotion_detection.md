# Emotion Detection Scanner

The Emotion Detection Scanner analyzes model outputs to detect emotional content using the roberta-base-go_emotions model. It can identify 28 different emotions and can be configured to flag outputs containing specific emotions.

## Attack scenario

This scanner helps ensure that model outputs maintain appropriate emotional tone and don't contain harmful emotional content. It's particularly useful for:
- Preventing emotionally charged or inappropriate responses
- Detecting emotionally manipulative content in outputs
- Ensuring consistent emotional tone in AI responses
- Blocking outputs with negative emotions that could be harmful

## How it works

The scanner uses the same roberta-base-go_emotions model as the input scanner to detect 28 different emotions in model outputs. It can be configured to flag outputs containing specific emotions or high-intensity emotional content.

## Usage

```python
from llm_guard.output_scanners import EmotionDetection

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
emotion_analysis = scanner.get_emotion_analysis(model_output)

# Scan with full output mode
scanner = EmotionDetection(threshold=0.5, return_full_output=True)
sanitized_output, is_valid, risk_score, full_analysis = scanner.scan_with_full_output(prompt, model_output)

sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Parameters

Same as input scanner:
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
python benchmarks/run.py output EmotionDetection
```

## Example

```python
from llm_guard.output_scanners import EmotionDetection

# Create scanner with default settings (blocks negative emotions)
scanner = EmotionDetection(threshold=0.5)

# Test model outputs
outputs = [
    "I don't have a specific answer for you but I will try to help.",
    "I am so happy to assist you with this question!",
    "I am really angry about this situation and cannot help.",
    "I am feeling sad and disappointed about this request."
]

for output in outputs:
    sanitized_output, is_valid, risk_score = scanner.scan("", output)
    print(f"Output: {output}")
    print(f"Valid: {is_valid}, Risk Score: {risk_score:.2f}")
    print()
```

Output:
```text
Output: I don't have a specific answer for you but I will try to help.
Valid: True, Risk Score: 0.00

Output: I am so happy to assist you with this question!
Valid: True, Risk Score: 0.00

Output: I am really angry about this situation and cannot help.
Valid: False, Risk Score: 0.85

Output: I am feeling sad and disappointed about this request.
Valid: False, Risk Score: 0.72
```

## Full Emotion Analysis

The scanner also supports full emotion analysis mode that returns all detected emotions with their scores:

```python
from llm_guard.output_scanners import EmotionDetection

# Get full emotion analysis
scanner = EmotionDetection(threshold=0.5)
emotion_analysis = scanner.get_emotion_analysis("I am so happy to help you with this!")
print(emotion_analysis)
# Output: {'joy': 0.85, 'excitement': 0.72, 'optimism': 0.45, ...}

# Scan with full output mode
scanner = EmotionDetection(threshold=0.5, return_full_output=True)
sanitized_output, is_valid, risk_score, full_analysis = scanner.scan_with_full_output("", "I am angry and sad!")
print(f"Valid: {is_valid}, Risk: {risk_score:.2f}")
print(f"Full Analysis: {full_analysis}")
# Output: Valid: False, Risk: 0.75
# Full Analysis: {'anger': 0.82, 'sadness': 0.65, 'disappointment': 0.45, ...}
```
