def generate_structure(model_type, credits):

    credits = int(credits)

    if model_type == "standard":

        total_units = credits + 1
        topic_count = 5

    elif model_type == "micro":

        total_units = credits * 4
        topic_count = 3

    elif model_type == "custom":

        total_units = credits
        topic_count = 4

    else:
        return {
            "error": f"Unknown model type: {model_type}"
        }

    units = []

    for i in range(1, total_units + 1):

        units.append({
            "unitNumber": i,
            "unitTitle": f"Unit {i}",
            "topicCount": topic_count,
            "shortDescription": f"Generated content for Unit {i}"
        })

    return {
        "totalUnits": total_units,
        "units": units
    }