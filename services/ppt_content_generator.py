import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def generate_unit_slides(
    unit_name,
    topics
):

    topics_text = "\n".join(
        f"- {topic}"
        for topic in topics
    )

    prompt = f"""
Create a university PowerPoint presentation.

Unit:
{unit_name}

Topics:
{topics_text}

Instructions:

1. Cover EVERY topic.
2. Generate approximately 5 slides per topic.
3. Use detailed academic content.
4. Each slide must have:
   - title
   - 4 to 6 bullet points
5. Return ONLY valid JSON.

Format:

{{
    "slides":[
        {{
            "title":"Slide Title",
            "bullets":[
                "point 1",
                "point 2"
            ]
        }}
    ]
}}
"""

    response = model.generate_content(
        prompt
    )

    response_text = response.text

    response_text = (
        response_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(
        response_text
    )