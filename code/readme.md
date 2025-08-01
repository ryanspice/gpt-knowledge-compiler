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
1. Run the script using Python:
   ```bash
   python gpt_compiler.py
   ```
2. Select the directories and files to process.
3. Name the output file and choose the output format.
4. Optional flags:
   - `--debug`: Enable debug mode for verbose logging.

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
