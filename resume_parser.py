import fitz  # PyMuPDF
import io

def extract_text_from_pdf(file):
    # If file is a path string
    if isinstance(file, str):
        doc = fitz.open(file)
    else:
        # If file is a Streamlit UploadedFile object
        doc = fitz.open(stream=file.read(), filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()
    return text
