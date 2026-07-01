import os

from services.ppt_content_generator import (
    generate_unit_slides
)

from services.ppt_generator import (
    create_ppt
)


def generate_unit_presentation(
    unit_name,
    topics,
    output_folder="generated_ppts"
):

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    print(
    f"Generating PPT for {unit_name}"
)

    result = generate_unit_slides(
        unit_name,
        topics
    )

    all_slides = result["slides"]

    safe_name = unit_name.replace(
        ":",
        ""
    ).replace(
        "/",
        "_"
    )

    ppt_path = os.path.join(
        output_folder,
        f"{safe_name}.pptx"
    )

    create_ppt(
        all_slides,
        ppt_path
    )

    return ppt_path