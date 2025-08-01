# Enhanced Data Processing Script

## Overview
This script processes various file types within a directory, extracting and organizing data, especially from image files. It supports formats such as JSON, CSV, XML, TXT, Markdown, DOCX, and common image formats like BMP, JPEG, PNG, GIF, and more. The script includes features like OCR (Optical Character Recognition) for images and provides descriptive data about each processed file.

## Requirements
- Python 3.x
- Libraries: Pillow, Pytesseract, Tqdm, Termcolor, PyYAML, Python-docx
- Tesseract OCR (for OCR functionalities)

## Installation
Install the required Python libraries using pip:
```bash
pip install Pillow pytesseract tqdm termcolor pyyaml python-docx
```
Install Tesseract OCR. Follow the instructions here: [Tesseract OCR Installation](https://github.com/tesseract-ocr/tesseract).


## Usage
1. Place the script in the directory containing the files you want to process.
2. Run the script using Python:
   ```bash
   python script_name.py
   ```
3. Optional flags:
   - `--debug`: Enable debug mode for verbose logging.



4. Optional venv setup:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```



## USAGE 2

.\venv\Scripts\activate



## Flow

1. Gather knowledge sources into folder.
   - gpt-crawler
   - custom gpts
   - reddit posts
   - documentation
   - code examples
   - images, pdfs, etc.
2. Execute python .  script to process all files in the folder.
   - Extract text from all files.
   - Extract data from structured files (json, csv, xml, etc.)
   - Extract data from images (OCR)
   - Organize data into a structured format.
   - Log progress and important information.
   - Handle errors gracefully.
   - Runs gpt-crawler, for example with the following command:
      ```bash
      python ./src --url "https://scriptgpt.wiki/" --match "https://scriptgpt.wiki/**" --project "ScriptGPT"
      ```

## Features
- Processes files in various formats, extracting relevant data.
- Performs OCR on image files to extract text.
- Organizes extracted data into a structured format.
- Logs progress and important information with colored outputs.
- Handles errors gracefully, providing informative messages for troubleshooting.

## File Support
- **Text Files**: `.txt`, `.md`
- **Document Files**: `.doc`, `.docx`
- **Data Files**: `.json`, `.csv`, `.xml`, `.yaml`
- **Image Files**: `.bmp`, `.jpeg`, `.png`, `.gif`, `.ico`, `.svg`, `.psd`, `.pdf`
- Additional image processing and OCR support for image files.

## Configuration
The script can be configured via a `config.json` file, allowing customization of log levels, output paths, and other settings.

## Logging
Detailed logging is provided, including debug information if the debug mode is enabled. Logs can be viewed in the console and optionally saved to a file.

## Contributing
Contributions to enhance the script's capabilities are welcome. Please ensure to follow the existing code structure and style for consistency.

## License
[Specify your license or terms of use]

## Contact
[Your Contact Information]

## Acknowledgments
- Tesseract OCR for OCR capabilities.
- Pillow and other Python libraries that made this script possible.