"""Standard Model enforcement: redistribute extracted syllabus topics across model units."""


def flatten_extracted_topics(units_data: dict) -> tuple[list[str], list[str]]:
    """
    Collect all extracted topics in document order.

    Returns:
        (topics, warnings)
    """
    warnings: list[str] = []
    topics: list[str] = []

    if not isinstance(units_data, dict):
        warnings.append("Extracted syllabus data is invalid; expected a unit map.")
        return topics, warnings

    for unit_name, unit_topics in units_data.items():
        if not isinstance(unit_topics, list):
            warnings.append(f'Skipped invalid topic list for "{unit_name}".')
            continue

        for topic in unit_topics:
            if topic is None:
                continue

            cleaned = str(topic).strip()
            if cleaned:
                topics.append(cleaned)

    if not topics and units_data:
        warnings.append(
            "No topics were found in the uploaded syllabus. "
            "Standard Model topic counts will be used."
        )

    return topics, warnings


def count_extracted_units(units_data: dict) -> int:
    """Count unit keys in extracted syllabus data."""
    if not isinstance(units_data, dict) or units_data.get("error"):
        return 0

    return sum(
        1
        for unit_topics in units_data.values()
        if isinstance(unit_topics, list)
    )


def distribute_topics_evenly(topics: list[str], unit_count: int) -> list[list[str]]:
    """
    Distribute topics across units with counts differing by at most one.
    Preserves topic order and guarantees no topic loss.
    """
    if unit_count <= 0:
        raise ValueError("unit_count must be greater than 0.")

    if not topics:
        return [[] for _ in range(unit_count)]

    base_size, extra_units = divmod(len(topics), unit_count)
    distributed: list[list[str]] = []
    index = 0

    for unit_index in range(unit_count):
        bucket_size = base_size + (1 if unit_index < extra_units else 0)
        distributed.append(topics[index : index + bucket_size])
        index += bucket_size

    return distributed


def validate_topic_distribution(
    original_topics: list[str],
    distributed: list[list[str]],
    unit_count: int,
) -> list[str]:
    """Validate that redistribution preserved every topic."""
    warnings: list[str] = []

    if len(distributed) != unit_count:
        warnings.append(
            f"Distribution mismatch: expected {unit_count} unit buckets, "
            f"got {len(distributed)}."
        )

    flattened = [topic for bucket in distributed for topic in bucket]

    if len(flattened) != len(original_topics):
        warnings.append(
            f"Topic loss detected: {len(original_topics)} extracted, "
            f"{len(flattened)} after distribution."
        )

    if flattened != original_topics:
        warnings.append(
            "Topic order changed during redistribution. "
            "All topics are preserved but sequencing may differ from the PDF."
        )

    return warnings


def enforce_standard_model(structure: dict, units_data: dict | None = None) -> dict:
    """
    Enforce Standard Model unit count while preserving extracted syllabus topics.

    Standard Model controls totalUnits; extracted topics are redistributed evenly
    across those units with no loss.
    """
    warnings: list[str] = []
    units = structure.get("units", [])
    unit_count = structure.get("totalUnits", len(units))

    enforcement = {
        "standardModelUnits": unit_count,
        "extractedUnits": 0,
        "totalTopicsExtracted": 0,
        "topicsPreserved": True,
        "topicsApplied": False,
    }

    if not units_data:
        enriched_units = [
            {**unit, "topics": unit.get("topics", [])}
            for unit in units
        ]
        return {
            **structure,
            "units": enriched_units,
            "warnings": warnings,
            "enforcement": enforcement,
        }

    if units_data.get("error"):
        warnings.append(
            f"Topic extraction failed: {units_data['error']}. "
            "Standard Model structure will be used without extracted topics."
        )
        enriched_units = [
            {**unit, "topics": unit.get("topics", [])}
            for unit in units
        ]
        return {
            **structure,
            "units": enriched_units,
            "warnings": warnings,
            "enforcement": enforcement,
        }

    extracted_unit_count = count_extracted_units(units_data)
    all_topics, extract_warnings = flatten_extracted_topics(units_data)
    warnings.extend(extract_warnings)

    enforcement["extractedUnits"] = extracted_unit_count
    enforcement["totalTopicsExtracted"] = len(all_topics)

    if extracted_unit_count != unit_count:
        warnings.append(
            f"The uploaded syllabus contains {extracted_unit_count} unit(s), "
            f"but the Standard Model requires {unit_count} unit(s) "
            f"(credits + 1). All {len(all_topics)} extracted topic(s) will be "
            "redistributed across the Standard Model units."
        )

    if all_topics:
        distributed = distribute_topics_evenly(all_topics, unit_count)
        distribution_warnings = validate_topic_distribution(
            all_topics,
            distributed,
            unit_count,
        )
        warnings.extend(distribution_warnings)
        enforcement["topicsApplied"] = True
        enforcement["topicsPreserved"] = (
            len([topic for bucket in distributed for topic in bucket]) == len(all_topics)
        )
    else:
        distributed = [[] for _ in range(unit_count)]

    enriched_units = []
    for unit, unit_topics in zip(units, distributed):
        enriched_units.append(
            {
                **unit,
                "topicCount": len(unit_topics) if unit_topics else unit.get("topicCount", 0),
                "topics": unit_topics,
            }
        )

    return {
        **structure,
        "units": enriched_units,
        "warnings": warnings,
        "enforcement": enforcement,
    }
