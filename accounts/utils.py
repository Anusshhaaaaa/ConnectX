"""
Utility functions for ConnectX application
- AI-based Toxic content detection (Trained ML Model)
- Safer rewrite generation
"""

import os
import pickle
import re
from google import genai

from django.conf import settings
from PIL import Image
import base64
import io

client = genai.Client(api_key=settings.GEMINI_API_KEY)


# ==========================================================
# 🤖 LOAD TRAINED AI MODEL
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "toxicity_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))


# ==========================================================
# 🧠 AI TOXICITY DETECTION
# ==========================================================

def detect_toxic_content(text):
    """
    Uses trained ML model to detect toxicity.
    Returns: (is_toxic: bool, toxic_score: float)
    """
    if not text:
        return False, 0.0

    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    probability = model.predict_proba(text_vec)[0][1]

    is_toxic = probability > 0.83
    toxic_score = float(probability)

    return is_toxic, toxic_score




# ==========================================================
# ✨ SAFER REWRITE (Simple Clean Version)
# ==========================================================

def get_safer_alternative(text, is_toxic):
    if not text or not is_toxic:
        return text

    print("🔥 Gemini rewrite triggered")

    try:
        prompt = f"""
        Rewrite the following message in a respectful and non-toxic way.
        Keep the meaning but remove insults, hate, or aggression.

        Message:
        "{text}"

        Provide only the rewritten sentence.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        rewritten = response.text

        print("🔥 Gemini response:", rewritten)

        return rewritten.strip()

    except Exception as e:
        print("❌ Gemini error:", e)
        return "Unable to generate safer alternative."

# ==========================================================
# ⚠️ TOXIC WARNINGS (AI-Based Threshold)
# ==========================================================

def get_toxic_warnings(text, score):
    warnings = []

    if score > 0.7:
        severity = "High"
    elif score > 0.4:
        severity = "Medium"
    elif score > 0.2:
        severity = "Low"
    else:
        return warnings

    warnings.append({
        "severity": severity,
        "message": f"This content has a {severity} toxicity probability ({round(score, 2)})."
    })

    return warnings


# ==========================================================
# 📝 PROCESS USER POST
# ==========================================================

def process_user_post(text, skip_detection=False):

    # If user is posting already sanitized text
    if skip_detection:
        return {
            "original_text": text,
            "is_toxic": False,
            "toxicity_score": 0.0,
            "safer_text": text,
            "warnings": []
        }

    is_toxic, score = detect_toxic_content(text)
    safer_text = get_safer_alternative(text, is_toxic)
    warnings = get_toxic_warnings(text, score)

    return {
        "original_text": text,
        "is_toxic": is_toxic,
        "toxicity_score": score,
        "safer_text": safer_text,
        "warnings": warnings
    }

def debug_list_models():
    print("Listing available models...\n")
    for m in client.models.list():
        print(m.name)

from PIL import Image

def analyze_image_toxicity(image_file):
    print("🖼 Image toxicity check triggered")

    try:
        image = Image.open(image_file)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                "Analyze this image. Does it contain toxic, hateful, violent, abusive, or inappropriate content? Respond with YES or NO and briefly explain.",
                image
            ],
        )

        result_text = response.text.strip()
        print("🖼 Gemini image response:", result_text)

        is_toxic = "YES" in result_text.upper()

        return {
            "is_toxic": is_toxic,
            "reason": result_text
        }

    except Exception as e:
        print("❌ Image Gemini error:", e)

        return {
            "is_toxic": False,
            "reason": "Unable to analyze image."
        }

    except Exception as e:
        print("❌ Image Gemini error:", e)
        return "Unable to analyze image."      

