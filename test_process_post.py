# test_process_post.py

from accounts.utils import process_user_post

# Sample posts to test
posts = [
    "You are an idiot and this is stupid!",
    "I love your work, keep it up!",
    "That movie was boring and trash.",
    "You are weird but harmless."
]

for post in posts:
    result = process_user_post(post)
    print("==================================================")
    print(f"Original Text: {result['original_text']}")
    print(f"Toxicity Detected: {result['is_toxic']}, Score: {result['toxicity_score']}")
    print(f"Safer Version: {result['safer_text']}")
    print("Warnings:")
    for w in result['warnings']:
        print(f"  - The word '{w['word']}' might be offensive. Consider using '{w['suggestion']}' instead.")
print("==================================================")
