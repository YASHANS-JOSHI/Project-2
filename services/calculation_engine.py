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