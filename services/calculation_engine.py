def calculate_ugc_metrics(
    credit,
    units,
    topics_per_unit
):

    total_learning_hours = credit * 30

    min_words = credit * 12000
    max_words = credit * 15000

    min_pages = credit * 60
    max_pages = credit * 80

    average_words = (
        min_words + max_words
    ) // 2

    words_per_unit = (
        average_words // units
        if units > 0
        else 0
    )

    words_per_topic = (
        words_per_unit // topics_per_unit
        if topics_per_unit > 0
        else 0
    )

    return {
        "learning_hours": total_learning_hours,
        "min_words": min_words,
        "max_words": max_words,
        "min_pages": min_pages,
        "max_pages": max_pages,
        "words_per_unit": words_per_unit,
        "words_per_topic": words_per_topic
    }


def calculate_slide_budget(
    topics,
    words_per_unit,
    words_per_topic,
):
    topic_count = len(
        [
            topic
            for topic in topics
            if str(topic).strip()
        ]
    )

    if words_per_topic < 500:
        depth_factor = 1
    elif words_per_topic <= 900:
        depth_factor = 2
    else:
        depth_factor = 3

    target_slides = (
        1
        + 1
        + (topic_count * depth_factor)
        + 1
    )

    if topic_count >= 8:
        target_slides += 1

    minimum_slides = max(6, topic_count + 3)
    maximum_slides = min(35, topic_count * 3 + 5)
    target_slides = max(
        minimum_slides,
        min(maximum_slides, target_slides),
    )

    return {
        "target_slides": target_slides,
        "min_slides": minimum_slides,
        "max_slides": maximum_slides,
        "depth_factor": depth_factor,
        "topic_count": topic_count,
        "words_per_unit": words_per_unit,
        "words_per_topic": words_per_topic,
    }