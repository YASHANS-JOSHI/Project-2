from content_generator import (
    generate_topic_slides
)

from ppt_generator import (
    create_ppt
)

result = generate_topic_slides(
    "Pattern Recognition Basics"
)

create_ppt(
    result["slides"],
    "pattern_recognition.pptx"
)

print(
    "PPT Generated Successfully"
)