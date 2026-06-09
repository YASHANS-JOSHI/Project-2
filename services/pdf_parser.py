import fitz
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\Yash\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    pdf = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    text = ""

    for page in pdf:

        page_text = page.get_text("text")

        text += page_text

    # If normal extraction worked
    if len(text.strip()) > 100:

        print("TEXT PDF DETECTED")

        return text

    print("OCR FALLBACK ACTIVATED")

    text = ""

    for page in pdf:

        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        image = Image.open(
            io.BytesIO(
                pix.tobytes("png")
            )
        )

        page_text = pytesseract.image_to_string(
            image
        )

        text += page_text + "\n"

    return text