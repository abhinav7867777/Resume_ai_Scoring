# ============================================================
# analyse_pdf.py
# Original mein: Google Gemini API
# Is version mein: OpenRouter API (Gemma 3n 4B Free)
# Same function name rakha hai — drop-in replacement!
# ============================================================

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key .env file se load hogi
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ── Model Options (sabhi FREE hain) ──
# "google/gemma-3n-e4b-it:free"           ← Gemma 3n 4B
# "meta-llama/llama-3.1-8b-instruct:free" ← Llama 3.1 8B
# "mistralai/mistral-7b-instruct:free"    ← Mistral 7B

MODEL = "nvidia/nemotron-3-super-120b-a12b:free"  # Most stable free model

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def analyse_resume_gemini(resume_content, job_description):
    """
    Original Gemini function ki jagah OpenRouter use karta hai.
    Same function name rakha — main.py mein kuch change nahi karna padega!
    """

    # ── Same prompt format as original ──
    prompt = f"""
    You are a professional resume analyzer.

    Resume:
    {resume_content}

    Job Description:
    {job_description}

    Task:
    - Analyze the resume against the job description.
    - Give a match score out of 100.
    - Highlight missing skills or experiences.
    - Suggest improvements.

    Return the result in structured format:
    Match Score: XX/100
    Missing Skills:
    - ...
    Suggestions:
    - ...
    Summary:
    ...
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Resume Analyzer"
    }

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional resume analyzer. Give structured analysis with match score, missing skills, and suggestions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=body,
            timeout=30
        )

        if response.status_code == 401:
            return "❌ Error: API Key galat hai! .env file mein OPENROUTER_API_KEY check karo."

        if response.status_code == 429:
            return "❌ Error: Rate limit! 2 minute baad dobara try karo."

        if response.status_code == 503:
            # Fallback to Mistral
            body["model"] = "openrouter/free"
            response = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=30)

        if not response.ok:
            err = response.json().get("error", {}).get("message", f"HTTP {response.status_code}")
            return f"❌ API Error: {err}"

        data = response.json()
        result_text = data["choices"][0]["message"]["content"]
        return result_text

    except requests.exceptions.ConnectionError:
        return "❌ Error: Internet connection nahi hai ya OpenRouter down hai."
    except requests.exceptions.Timeout:
        return "❌ Error: Request timeout! Dobara try karo."
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"
