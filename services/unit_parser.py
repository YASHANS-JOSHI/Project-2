import re


def extract_units_and_topics(text):

    units = {}

    current_unit = None

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if re.match(
            r"^(UNIT[\s\-]*[IVX0-9]+|Unit\s*\d+|Module\s*\d+)",
            line,
            re.IGNORECASE
        ):

            current_unit = line

            units[current_unit] = []

        elif current_unit:

            units[current_unit].append(line)

    return units