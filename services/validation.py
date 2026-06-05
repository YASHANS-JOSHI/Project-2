def validate_course_form(
    program_name: str,
    course_name: str,
    credit: int | None,
    model_label: str | None,
) -> list[str]:
    """Validate required course form fields. Returns a list of error messages."""
    errors: list[str] = []

    if not program_name or not program_name.strip():
        errors.append("Program Name is required.")

    if not course_name or not course_name.strip():
        errors.append("Course Name is required.")

    if credit is None:
        errors.append("Credits is required.")

    if not model_label or not model_label.strip():
        errors.append("Model selection is required.")

    return errors
