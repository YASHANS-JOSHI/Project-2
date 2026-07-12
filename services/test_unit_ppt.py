from services.calculation_engine import calculate_ugc_metrics
from services.unit_ppt_generator import generate_unit_presentation

unit_name = "Unit 1 Introduction to AI"

topics = [
    "History of AI",
    "Applications of AI",
    "Intelligent Agents",
    "Problem Solving",
]

ugc = calculate_ugc_metrics(
    credit=3,
    units=4,
    topics_per_unit=len(topics),
)

ppt_path = generate_unit_presentation(
    unit_name=unit_name,
    topics=topics,
    words_per_unit=ugc["words_per_unit"],
    words_per_topic=ugc["words_per_topic"],
    unit_number=1,
    course_name="Introduction to AI",
)

print("PPT CREATED:", ppt_path)
