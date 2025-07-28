"""
Example demonstrating the Emotion Detection scanners for both input and output.

This example shows how to use the EmotionDetection scanner to detect and block
negative emotions in prompts and model outputs.
"""

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import EmotionDetection
from llm_guard.output_scanners import EmotionDetection as OutputEmotionDetection

# Configure emotion detection scanners
input_emotion_scanner = EmotionDetection(
    threshold=0.5,
    blocked_emotions=[
        "anger",
        "annoyance",
        "disappointment",
        "disapproval",
        "disgust",
        "embarrassment",
        "fear",
        "grief",
        "nervousness",
        "remorse",
        "sadness",
    ],
)

output_emotion_scanner = OutputEmotionDetection(
    threshold=0.5,
    blocked_emotions=[
        "anger",
        "annoyance",
        "disappointment",
        "disapproval",
        "disgust",
        "embarrassment",
        "fear",
        "grief",
        "nervousness",
        "remorse",
        "sadness",
    ],
)


def test_input_scanning():
    """Test input scanning with different emotional content."""

    # Test cases with different emotional content
    test_prompts = [
        "Just a simple question about the weather.",
        "I am so happy to learn about this topic!",
        "I am absolutely furious about this situation!",
        "This makes me feel sad and disappointed.",
        "I am nervous about the upcoming test.",
        "I am so excited to help you with this!",
    ]

    print("=== Input Emotion Detection Test ===")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")

        try:
            sanitized_prompt, is_valid, risk_score = scan_prompt([input_emotion_scanner], prompt)
            if is_valid:
                print(f"✅ Valid (Risk: {risk_score:.2f})")
            else:
                print(f"❌ Blocked (Risk: {risk_score:.2f})")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_output_scanning():
    """Test output scanning with different emotional content."""

    # Test cases with different emotional content in model outputs
    test_outputs = [
        "I don't have a specific answer for you but I will try to help.",
        "I am so happy to assist you with this question!",
        "I am really angry about this situation and cannot help.",
        "I am feeling sad and disappointed about this request.",
        "I am nervous about providing this information.",
        "I am excited to help you with this interesting question!",
    ]

    print("\n=== Output Emotion Detection Test ===")
    for i, output in enumerate(test_outputs, 1):
        print(f"\nTest {i}: {output}")

        try:
            sanitized_output, is_valid, risk_score = scan_output(
                [output_emotion_scanner], "", output
            )
            if is_valid:
                print(f"✅ Valid (Risk: {risk_score:.2f})")
            else:
                print(f"❌ Blocked (Risk: {risk_score:.2f})")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_custom_emotion_blocking():
    """Test custom emotion blocking configurations."""

    print("\n=== Custom Emotion Blocking Test ===")

    # Block only specific emotions
    custom_scanner = EmotionDetection(
        threshold=0.5,
        blocked_emotions=["anger", "fear"],  # Only block anger and fear
    )

    test_prompts = [
        "I am so angry about this!",
        "I am feeling sad but that's okay.",
        "I am scared of the dark.",
        "I am happy and excited!",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")

        try:
            sanitized_prompt, is_valid, risk_score = scan_prompt([custom_scanner], prompt)
            if is_valid:
                print(f"✅ Valid (Risk: {risk_score:.2f})")
            else:
                print(f"❌ Blocked (Risk: {risk_score:.2f})")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_no_emotion_blocking():
    """Test scanner with no blocked emotions."""

    print("\n=== No Emotion Blocking Test ===")

    # Allow all emotions
    permissive_scanner = EmotionDetection(
        threshold=0.5,
        blocked_emotions=[],  # No blocked emotions
    )

    test_prompts = [
        "I am so angry about this!",
        "I am feeling sad and disappointed.",
        "I am happy and excited!",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")

        try:
            sanitized_prompt, is_valid, risk_score = scan_prompt([permissive_scanner], prompt)
            if is_valid:
                print(f"✅ Valid (Risk: {risk_score:.2f})")
            else:
                print(f"❌ Blocked (Risk: {risk_score:.2f})")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_full_emotion_analysis():
    """Test the full emotion analysis functionality."""

    print("\n=== Full Emotion Analysis Test ===")

    # Create scanner with full output mode
    full_output_scanner = EmotionDetection(threshold=0.5, return_full_output=True)

    test_prompts = [
        "I am so happy and excited about this!",
        "I am absolutely furious and sad about this situation!",
        "I am feeling neutral about this.",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")

        try:
            # Get full emotion analysis
            emotion_analysis = full_output_scanner.get_emotion_analysis(prompt)
            print(f"Emotion Analysis: {emotion_analysis}")

            # Scan with full output
            sanitized_prompt, is_valid, risk_score, full_analysis = (
                full_output_scanner.scan_with_full_output(prompt)
            )
            print(f"Valid: {is_valid}, Risk: {risk_score:.2f}")
            print(f"Full Analysis: {full_analysis}")

        except Exception as e:
            print(f"❌ Error: {e}")


def test_output_full_emotion_analysis():
    """Test the full emotion analysis functionality for outputs."""

    print("\n=== Output Full Emotion Analysis Test ===")

    # Create scanner with full output mode
    full_output_scanner = OutputEmotionDetection(threshold=0.5, return_full_output=True)

    test_outputs = [
        "I am so happy to help you with this!",
        "I am really angry and disappointed about this request!",
        "I am feeling neutral about this question.",
    ]

    for i, output in enumerate(test_outputs, 1):
        print(f"\nTest {i}: {output}")

        try:
            # Get full emotion analysis
            emotion_analysis = full_output_scanner.get_emotion_analysis(output)
            print(f"Emotion Analysis: {emotion_analysis}")

            # Scan with full output
            sanitized_output, is_valid, risk_score, full_analysis = (
                full_output_scanner.scan_with_full_output("", output)
            )
            print(f"Valid: {is_valid}, Risk: {risk_score:.2f}")
            print(f"Full Analysis: {full_analysis}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Emotion Detection Scanner Example")
    print("=" * 50)

    # Run all tests
    test_input_scanning()
    test_output_scanning()
    test_custom_emotion_blocking()
    test_no_emotion_blocking()
    test_full_emotion_analysis()
    test_output_full_emotion_analysis()

    print("\n" + "=" * 50)
    print("Example completed!")
