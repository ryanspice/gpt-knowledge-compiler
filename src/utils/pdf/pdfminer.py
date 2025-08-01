import fitz  # PyMuPDF
import logging
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_with_ocr(pdf_path):
    """
    Extracts text from a PDF, using OCR if necessary.
    :param pdf_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        # Try to extract text using regular text extraction
        page_text = page.get_text()
        if not page_text.strip():  # If no text found, attempt OCR
            pix = page.get_pixmap()
            page_text = pix.extract_text()

        text += page_text + "\n"

    return text

def extract_metadata(pdf_path):
    """
    Extracts metadata from a PDF file.
    :param pdf_path: Path to the PDF file.
    :return: Metadata as a dictionary.
    """
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    return metadata

def convert_text_to_json(text):
    """
    Converts extracted text to a structured JSON format.
    :param text: Extracted text as a string.
    :return: A JSON representation of the text.
    """
    # Example of structuring text; customize as needed
    paragraphs = text.split('\n')
    structured_data = {"content": paragraphs}
    return structured_data

def pdf_to_json(pdf_path):
    """
    Converts a PDF file to JSON format, including OCR and metadata.
    :param pdf_path: Path to the PDF file.
    :return: JSON representation including content and metadata.
    """
    try:
        text = extract_text_with_ocr(pdf_path)
        metadata = extract_metadata(pdf_path)
        json_data = {
            "metadata": metadata,
            "content": convert_text_to_json(text)
        }
        return json_data
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return None

if __name__ == "__main__":
    pdf_path = 'path_to_your_pdf.pdf'
    json_data = pdf_to_json(pdf_path)

    if json_data:
        # Print or save JSON data
        print(json.dumps(json_data, indent=4))
