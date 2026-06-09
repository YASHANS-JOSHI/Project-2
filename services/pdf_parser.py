import fitz

def extract_text_from_pdf(uploaded_file):

    print("PDF PARSER CALLED")

    file_bytes = uploaded_file.read()

    print("BYTES =", len(file_bytes))

    pdf = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    print("PAGES =", len(pdf))

    text = ""

    for i, page in enumerate(pdf):

        page_text = page.get_text("text")

        print(
            f"PAGE {i+1} LENGTH =",
            len(page_text)
        )

        text += page_text

    print(
        "TOTAL LENGTH =",
        len(text)
    )

    return text