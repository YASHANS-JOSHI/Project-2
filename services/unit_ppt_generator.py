import os
import re

from services.ppt_content_generator import (
    PptContentError,
    generate_unit_slides,
)
from services.ppt_generator import create_ppt


class UnitPresentationError(Exception):
    pass


def _safe_filename(unit_number, unit_name):
    title_part = re.sub(
        r'[<>:"/\\|?*\n\r\t]+',
        " ",
        unit_name,
    )
    title_part = re.sub(r"\s+", "_", title_part.strip())
    title_part = re.sub(r"_+", "_", title_part).strip("_")

    if not title_part:
        title_part = "Unit"

    number = int(unit_number) if unit_number is not None else 0
    return f"Unit_{number:02d}_{title_part}.pptx"


def generate_unit_presentation(
    unit_name,
    topics,
    words_per_unit,
    words_per_topic,
    unit_number=None,
    course_name=None,
    academic_level=None,
    output_folder="generated_ppts",
):
    if not topics:
        raise UnitPresentationError(
            f"Unit '{unit_name}' has no topics."
        )

    os.makedirs(output_folder, exist_ok=True)

    print(
        f"Generating PPT for {unit_name} "
        f"({len(topics)} topics, "
        f"{words_per_unit} words/unit budget, "
        f"{words_per_topic} words/topic budget)"
    )

    result = generate_unit_slides(
        unit_name=unit_name,
        topics=topics,
        words_per_unit=words_per_unit,
        words_per_topic=words_per_topic,
        course_name=course_name,
        unit_number=unit_number,
        academic_level=academic_level,
    )

    all_slides = result.get("slides", [])

    if not all_slides:
        raise UnitPresentationError(
            f"No slides returned for unit '{unit_name}'."
        )

    ppt_filename = _safe_filename(unit_number, unit_name)
    ppt_path = os.path.join(output_folder, ppt_filename)

    create_ppt(all_slides, ppt_path)

    print(
        f"Created {ppt_path} with {len(all_slides)} slides"
    )

    return ppt_path
