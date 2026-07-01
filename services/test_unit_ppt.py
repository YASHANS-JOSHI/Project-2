print("TEST FILE STARTED")
from services.unit_ppt_generator import (
    generate_unit_presentation
)

unit_name = "Unit 1 Introduction to AI"

topics = [
    "History of AI",
    "Applications of AI",
    "Intelligent Agents",
    "Problem Solving"
]

ppt_path = generate_unit_presentation(
    unit_name,
    topics
)

print(
    "PPT CREATED:",
    ppt_path
)