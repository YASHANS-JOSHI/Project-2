import json
import google.generativeai as genai


import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def extract_units_topics_with_gemini(
    syllabus_text
):

    print("========== GEMINI INPUT ==========")
    print("TEXT LENGTH =", len(syllabus_text))
    print(syllabus_text[:2000])
    print("==================================")

    if not syllabus_text.strip():

        return {
            "error": "Empty syllabus text"
        }

    prompt = f"""
You are an academic syllabus parser.

Extract all units and their topics.

Return ONLY valid JSON.

Example:

{{
    "Unit 1": [
        "Definition and History of AI",
        "Applications of AI",
        "Intelligent Agents"
    ],
    "Unit 2": [
        "BFS",
        "DFS",
        "A* Search"
    ]
}}

Syllabus:

{syllabus_text}
"""

    response = model.generate_content(
        prompt
    )

    response_text = response.text.strip()

    print("========== GEMINI OUTPUT ==========")
    print(response_text)
    print("===================================")

    response_text = response_text.replace(
        "```json",
        ""
    )

    response_text = response_text.replace(
        "```",
        ""
    ).strip()

    try:

        return json.loads(
            response_text
        )

    except Exception:

        return {
            "error": "Failed to parse Gemini response",
            "raw_response": response_text
        }