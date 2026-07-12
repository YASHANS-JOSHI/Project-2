from services.calculation_engine import calculate_ugc_metrics
from services.unit_ppt_generator import generate_unit_presentation

units_data = {
    "Unit 1": [
        "History of AI",
        "Applications of AI",
        "Intelligent Agents",
    ],
    "Unit 2": [
        "BFS",
        "DFS",
        "A Star Search",
    ],
}

ugc = calculate_ugc_metrics(
    credit=3,
    units=len(units_data),
    topics_per_unit=3,
)

ppt_files = {}

for unit_number, (unit_name, topics) in enumerate(
    units_data.items(),
    start=1,
):
    ppt_path = generate_unit_presentation(
        unit_name=unit_name,
        topics=topics,
        words_per_unit=ugc["words_per_unit"],
        words_per_topic=ugc["words_per_topic"],
        unit_number=unit_number,
        course_name="Sample Course",
    )
    ppt_files[unit_name] = ppt_path

print(ppt_files)
