# test_run.py
# Quick test runner for ConnectX utility functions

from accounts.utils import detect_toxic_content, get_safer_alternative, get_toxic_warnings

# Example texts to test
texts_to_test = [
    "You are an idiot and this is stupid!",
    "I love your work, keep it up!",
    "That movie was boring and trash.",
    "You are weird but harmless."
]

for text in texts_to_test:
    print("="*50)
    print(f"Original Text: {text}")

    # Detect toxicity
    is_toxic, score = detect_toxic_content(text)
    print(f"Toxicity Detected: {is_toxic}, Score: {score}")

    # Get safer alternative
    safer_version = get_safer_alternative(text)
    print(f"Safer Version: {safer_version}")

    # Get warnings
    warnings = get_toxic_warnings(text)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - The word '{w['word']}' might be offensive. Consider using '{w['suggestion']}' instead.")
    else:
        print("Warnings:")
print("="*50)
