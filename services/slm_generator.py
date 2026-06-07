def generate_slm_structure(
    units,
    topics_per_unit
):

    generated_units = []

    for i in range(
        1,
        units + 1
    ):

        topics = []

        for j in range(
            1,
            topics_per_unit + 1
        ):

            topics.append(
                f"Topic {j}"
            )

        unit = {
            "unit_title": f"Unit {i}",
            "introduction": (
                f"Introduction for Unit {i}"
            ),
            "learning_objectives": [
                "Understand concepts",
                "Apply knowledge",
                "Analyze problems"
            ],
            "topics": topics,
            "summary": (
                f"Summary of Unit {i}"
            ),
            "keywords": [
                "Keyword 1",
                "Keyword 2",
                "Keyword 3"
            ],
            "case_study": (
                f"Case Study for Unit {i}"
            ),
            "saqs": [
                "Question 1",
                "Question 2"
            ],
            "answers": [
                "Answer 1",
                "Answer 2"
            ],
            "references": [
                "Reference 1",
                "Reference 2"
            ]
        }

        generated_units.append(
            unit
        )

    return generated_units