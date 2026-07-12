"""
PPT slide content via Gemini.

Uses `google.generativeai` (legacy SDK) intentionally — syllabus parsing
(`gemini_parser.py`) still depends on it. Migrate both services together
when moving to `google.genai`.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions

from services.calculation_engine import calculate_slide_budget

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

DEBUG_DIR = Path("debug_responses")

SLIDES_GENERATION_CONFIG = genai.GenerationConfig(
    response_mime_type="application/json",
    temperature=0.3,
    max_output_tokens=16384,
)


class GeminiQuotaExceededError(Exception):
    def __init__(self, message, retry_seconds=None, is_daily_quota=False):
        super().__init__(message)
        self.retry_seconds = retry_seconds
        self.is_daily_quota = is_daily_quota


class PptContentError(Exception):
    """Controlled error for invalid or unusable Gemini slide content."""


def _normalize_topics(topics):
    normalized = []

    for topic in topics:
        if isinstance(topic, str):
            cleaned = topic.strip()
            if cleaned:
                normalized.append(cleaned)
        elif isinstance(topic, dict):
            label = (
                topic.get("title")
                or topic.get("name")
                or str(topic)
            ).strip()
            if label:
                normalized.append(label)
        else:
            label = str(topic).strip()
            if label:
                normalized.append(label)

    return normalized


def _build_unit_prompt(
    unit_name,
    topics,
    words_per_unit,
    words_per_topic,
    slide_budget,
    course_name=None,
    unit_number=None,
    academic_level=None,
):
    topics_text = "\n".join(
        f"{index}. {topic}"
        for index, topic in enumerate(topics, start=1)
    )

    course_line = course_name or "Not specified"
    level_line = academic_level or "Not specified"
    unit_number_line = unit_number if unit_number is not None else "Not specified"

    return f"""
Create one university PowerPoint presentation for a single academic unit.

Course name: {course_line}
Unit number: {unit_number_line}
Unit title: {unit_name}
Academic level: {level_line}

Complete ordered topic list:
{topics_text}

UGC/DEB academic depth budgets from the calculation engine:
- words_per_unit depth budget: {words_per_unit}
- words_per_topic depth budget: {words_per_topic}

IMPORTANT:
The academic word budgets above represent expected learning depth, conceptual
coverage, relative teaching depth, and content allocation guidance.
They are NOT literal output-length requirements.
Do NOT generate the full word budget verbatim.
Do NOT place thousands of words on slide bullets.

Presentation slide budget (deterministic target):
- Target total slides: {slide_budget["target_slides"]}
- Allowed range: {slide_budget["min_slides"]} to {slide_budget["max_slides"]}
- Suggested depth factor: {slide_budget["depth_factor"]} slides per topic on average

Coverage rules:
1. Preserve syllabus fidelity and topic order.
2. Every provided syllabus topic must be represented in at least one slide or
   explicitly covered within a clearly related slide.
3. Complex topics may receive multiple slides.
4. Simple closely related topics may share a slide when academically appropriate.
5. Never silently drop a topic.
6. Do not invent unrelated topics.
7. Include a title slide, learning objectives, topic coverage slides, and a
   final summary/review.
8. Keep slide bullets concise (3-5 bullets). Use speaker_notes for deeper teaching
   explanation, examples, and academic detail.
9. Explain concepts academically and use examples where useful.

Return ONLY valid JSON.
No markdown.
No ```json fences.
No commentary before JSON.
No commentary after JSON.
Exactly one JSON object.

Required JSON schema:
{{
  "unit_title": "{unit_name}",
  "slides": [
    {{
      "title": "Slide title",
      "bullets": [
        "Concise bullet 1",
        "Concise bullet 2"
      ],
      "speaker_notes": "Deeper teaching explanation for this slide."
    }}
  ]
}}
"""


def _strip_code_fences(response_text):
    cleaned = response_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```$", "", cleaned)

    return cleaned.strip()


def _extract_json_candidate(response_text):
    cleaned = _strip_code_fences(response_text)
    start = cleaned.find("{")

    if start == -1:
        raise json.JSONDecodeError(
            "No JSON object found",
            cleaned,
            0,
        )

    return cleaned[start:]


def _repair_json_text(json_text):
    return re.sub(r",\s*([}\]])", r"\1", json_text)


def parse_model_json(response_text):
    cleaned = _strip_code_fences(response_text)
    candidate = _extract_json_candidate(cleaned)

    attempts = (
        candidate,
        _repair_json_text(candidate),
    )

    last_error = None

    for attempt_text in attempts:
        try:
            decoder = json.JSONDecoder()
            data, end_index = decoder.raw_decode(attempt_text)
            remainder = attempt_text[end_index:].strip()

            if remainder:
                raise PptContentError(
                    "Gemini returned extra text after the JSON object."
                )

            if not isinstance(data, dict):
                raise PptContentError(
                    "Gemini response must be a single JSON object."
                )

            return data
        except (json.JSONDecodeError, PptContentError, ValueError) as error:
            last_error = error

    raise PptContentError(
        f"Could not parse Gemini JSON response: {last_error}"
    )


def _slide_text_blob(slide):
    parts = [
        slide.get("title", ""),
        slide.get("speaker_notes", ""),
    ]
    parts.extend(slide.get("bullets", []))
    return " ".join(str(part) for part in parts).lower()


def _check_topic_coverage(topics, slides):
    for topic in topics:
        topic_lower = topic.lower()
        topic_parts = [
            part.strip().lower()
            for part in re.split(r"[,;/]+", topic)
            if part.strip()
        ]

        matched = any(
            topic_lower in _slide_text_blob(slide)
            or any(
                part in _slide_text_blob(slide)
                for part in topic_parts
            )
            for slide in slides
        )

        if not matched:
            print(
                f"Warning: no slide content matched topic '{topic}'"
            )


def _validate_slides_payload(data, unit_name, topics):
    unit_title = str(
        data.get("unit_title")
        or data.get("unit_name")
        or unit_name
    ).strip()

    slides = data.get("slides")
    if not isinstance(slides, list):
        raise PptContentError(
            'Gemini response must include a "slides" array.'
        )

    validated_slides = []

    for slide in slides:
        if not isinstance(slide, dict):
            continue

        title = str(slide.get("title", "")).strip()
        bullets = slide.get("bullets")

        if not title or not isinstance(bullets, list):
            continue

        cleaned_bullets = [
            str(bullet).strip()
            for bullet in bullets
            if str(bullet).strip()
        ]

        if not cleaned_bullets:
            continue

        validated_slides.append(
            {
                "title": title,
                "bullets": cleaned_bullets,
                "speaker_notes": str(
                    slide.get("speaker_notes", "")
                ).strip(),
            }
        )

    if not validated_slides:
        raise PptContentError(
            f"No valid slides were returned for unit '{unit_title}'."
        )

    _check_topic_coverage(topics, validated_slides)

    return {
        "unit_title": unit_title,
        "slides": validated_slides,
    }


def _save_debug_response(unit_name, response_text, error):
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_name = re.sub(r'[<>:"/\\|?*]+', "_", unit_name).strip() or "unit"
    debug_path = DEBUG_DIR / f"{safe_name}_{timestamp}.txt"
    debug_path.write_text(
        f"ERROR: {error}\n\n--- RAW RESPONSE ---\n{response_text}",
        encoding="utf-8",
    )
    print(f"Saved invalid Gemini response to {debug_path}")


def _parse_slides_response(response_text, unit_name, topics):
    data = parse_model_json(response_text)
    return _validate_slides_payload(data, unit_name, topics)


def _extract_retry_seconds(error):
    match = re.search(
        r"retry in ([0-9.]+)s",
        str(error),
        flags=re.IGNORECASE,
    )
    return float(match.group(1)) if match else None


def _is_daily_quota_error(error):
    error_text = str(error).lower()
    return (
        "perday" in error_text
        or "free_tier_requests" in error_text
        or "generatecontentfree" in error_text.replace("_", "")
    )


def _call_gemini_once(prompt):
    try:
        return model.generate_content(
            prompt,
            generation_config=SLIDES_GENERATION_CONFIG,
        )
    except google_exceptions.ResourceExhausted as error:
        retry_seconds = _extract_retry_seconds(error)

        if _is_daily_quota_error(error):
            raise GeminiQuotaExceededError(
                "Gemini free-tier daily request limit reached. "
                "Wait until tomorrow, enable billing, or generate units "
                "one at a time.",
                retry_seconds=retry_seconds,
                is_daily_quota=True,
            ) from error

        raise GeminiQuotaExceededError(
            "Gemini rate limit reached. Please wait and try again.",
            retry_seconds=retry_seconds,
            is_daily_quota=False,
        ) from error


def _call_gemini(prompt):
    try:
        return _call_gemini_once(prompt)
    except GeminiQuotaExceededError as error:
        if error.is_daily_quota or not error.retry_seconds:
            raise

        time.sleep(min(error.retry_seconds, 30))
        return _call_gemini_once(prompt)


def generate_unit_slides(
    unit_name,
    topics,
    words_per_unit,
    words_per_topic,
    course_name=None,
    unit_number=None,
    academic_level=None,
):
    normalized_topics = _normalize_topics(topics)

    if not normalized_topics:
        raise PptContentError(
            f"Unit '{unit_name}' has no topics to generate slides for."
        )

    slide_budget = calculate_slide_budget(
        normalized_topics,
        words_per_unit,
        words_per_topic,
    )

    prompt = _build_unit_prompt(
        unit_name=unit_name,
        topics=normalized_topics,
        words_per_unit=words_per_unit,
        words_per_topic=words_per_topic,
        slide_budget=slide_budget,
        course_name=course_name,
        unit_number=unit_number,
        academic_level=academic_level,
    )

    print(
        f"Calling Gemini once for '{unit_name}' "
        f"({len(normalized_topics)} topics, "
        f"target {slide_budget['target_slides']} slides)"
    )

    response = _call_gemini(prompt)
    response_text = response.text

    try:
        return _parse_slides_response(
            response_text,
            unit_name,
            normalized_topics,
        )
    except PptContentError as error:
        _save_debug_response(unit_name, response_text, error)
        raise
