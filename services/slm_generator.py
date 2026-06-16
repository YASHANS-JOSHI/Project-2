def _placeholder_topics(topic_count: int) -> list[str]:
    return [f"Topic {index}" for index in range(1, topic_count + 1)]


def generate_slm_structure(units: list[dict]) -> list[dict]:
    """
    Build SLM blocks from the enforced unit structure.

    Uses extracted topics when available; otherwise falls back to placeholders.
    """
    generated_units = []

    for unit in units:
        unit_number = unit.get("unitNumber", len(generated_units) + 1)
        topics = unit.get("topics") or _placeholder_topics(unit.get("topicCount", 5))
        unit_title = unit.get("unitTitle") or f"Unit {unit_number}"
        short_description = unit.get(
            "shortDescription",
            f"Generated content for Unit {unit_number}",
        )

        generated_units.append(
            {
                "unit_number": unit_number,
                "unit_title": unit_title,
                "introduction": (
                    f"Introduction for {unit_title}. {short_description}"
                ),
                "learning_objectives": [
                    "Understand core concepts covered in this unit",
                    "Apply knowledge to practical scenarios",
                    "Analyze problems using unit topics",
                ],
                "topics": topics,
                "summary": f"Summary of {unit_title}",
                "keywords": topics[:3] if topics else ["Keyword 1", "Keyword 2", "Keyword 3"],
                "case_study": f"Case Study for {unit_title}",
                "saqs": [
                    "Question 1",
                    "Question 2",
                ],
                "answers": [
                    "Answer 1",
                    "Answer 2",
                ],
                "references": [
                    "Reference 1",
                    "Reference 2",
                ],
            }
        )

    return generated_units
