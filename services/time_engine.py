def calculate_time_distribution(
    units,
    topics_per_unit,
    learning_hours,
    time_per_unit=80
):

    total_unit_time = (
        units * time_per_unit
    )

    learning_minutes = (
        learning_hours * 60
    )

    if total_unit_time > learning_minutes:

        adjusted_time = (
            learning_minutes // units
        )

        adjusted_time = max(
            60,
            min(
                adjusted_time,
                90
            )
        )

        time_per_unit = adjusted_time

    time_per_topic = (
        time_per_unit // topics_per_unit
        if topics_per_unit > 0
        else 0
    )

    total_course_time = (
        units * time_per_unit
    )

    return {
        "time_per_unit": time_per_unit,
        "time_per_topic": time_per_topic,
        "total_course_time": total_course_time
    }