import sys
import os
import threading
import queue
import time
import zipfile
import tarfile
import py7zr
import psutil
import logging
import tempfile
import shutil
from pdf2image import convert_from_path
import pytesseract
import json
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supported archive extensions
ARCHIVE_EXTENSIONS = {
    '.zip': zipfile.ZipFile,
    '.tar': tarfile.open,
    '.tgz': lambda path: tarfile.open(path, 'r:gz'),
    '.tar.gz': lambda path: tarfile.open(path, 'r:gz'),
    '.7z': py7zr.SevenZipFile
}

def process_directory(directory, file_queue):
    """Recursively process directories to queue files and directories."""
    for root, _, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            file_queue.put(file_path)
            logging.info(f"Queued {file_path}")

def extract_archive(path, ext, temp_dir, file_queue):
    """Extract archives and queue the contents."""
    try:
        with ARCHIVE_EXTENSIONS[ext](path) as archive:
            extraction_path = os.path.join(temp_dir, os.path.basename(path))
            archive.extractall(extraction_path)
            logging.info(f"Extracted {path} to {extraction_path}")
            process_directory(extraction_path, file_queue)
    except Exception as e:
        logging.error(f"Error processing archive {path}: {str(e)}")
        return {'path': path, 'status': 'Failed', 'data': None, 'time_taken': 0}

def process_pdf(path):
    """Process PDFs and extract text using OCR."""
    try:
        logging.info(f"Processing PDF: {path}")
        images = convert_from_path(path)
        pdf_data = {'text': [pytesseract.image_to_string(image) for image in images]}
        logging.info(f"Finished processing PDF: {path}")
        return {'path': path, 'status': 'Success', 'data': pdf_data, 'time_taken': 0}
    except Exception as e:
        logging.error(f"Error processing PDF file {path}: {e}")
        return {'path': path, 'status': 'Failed', 'data': None, 'time_taken': 0}

def process_file(path, temp_dir, file_queue):
    """Process individual files and handle archives and PDFs."""
    start_time = time.time()
    _, ext = os.path.splitext(path)
    file_data = {'path': path, 'status': 'Success', 'data': None}

    if ext in ARCHIVE_EXTENSIONS:
        file_data = extract_archive(path, ext, temp_dir, file_queue) or file_data
    elif ext.lower() == '.pdf':
        file_data = process_pdf(path) or file_data

    file_data['time_taken'] = time.time() - start_time
    logging.info(f"Finished processing {path} in {file_data['time_taken']} seconds")
    return file_data

def worker(file_queue, result, temp_dir):
    while True:
        path = file_queue.get()
        if path is None:
            break
        result.append(process_file(path, temp_dir, file_queue))
        file_queue.task_done()

#
def start_parsing(CONFIG, directory):
    file_queue = queue.Queue()
    result = []
    temp_dir = tempfile.mkdtemp()

    try:
        process_directory(directory, file_queue)
        num_workers = min(4, os.cpu_count() or 1)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, file_queue, result, temp_dir) for _ in range(num_workers)]
            for _ in range(num_workers):
                file_queue.put(None)
            for future in futures:
                future.result()

        logging.info(f"CPU usage: {psutil.cpu_percent()}%")
        logging.info(f"Memory usage: {psutil.virtual_memory().percent}%")
    finally:
        shutil.rmtree(temp_dir)

    # Create the Markdown output instead of JSON
    output_md = compile_markdown(result, CONFIG)

    # Write the Markdown result to a file
    with open('sgpt-output.md', 'w') as f:
        f.write(output_md)

    # Write the results to a file
    # with open('sgpt-test-refactor.1.0.0.md', 'w') as f:
    #     json.dump(result, f, indent=4)

    return result


def compile_markdown(data, config):
    """
    Generate markdown output from the parsed data and configuration.
    """
    md_output = []

    # Header for the markdown file
    md_output.append(f"# Knowledge File for {config['project']} - {config['project_name']}")
    md_output.append(f"## Source Folder: {config['src_folder']}")
    md_output.append(f"## Output Folder: {config['output_folder']}")
    md_output.append(f"### URL: [{config['url']}]({config['url']})\n")

    # VARIABLES Section
    md_output.append("#### VARIABLES ####")
    md_output.append(f"NAME: {config['project']}")
    md_output.append(f"FILE: {config['project_name']}")
    md_output.append(f"TYPE: Text/Markdown")
    md_output.append(f"VERSION: 1.0.0")  # Assuming version is static here
    md_output.append(f"DATE: 2024-09-24")  # Assuming static date
    md_output.append(f"AUTHOR: ScriptGPT")  # Assuming static author
    md_output.append(f"GOAL: Track project file parsing activities and output refactoring details.")
    md_output.append(f"FOCUS: Refactoring, Analysis, Documentation")
    md_output.append(f"TAGS: Project, Refactoring, Analysis\n")

    # COMMANDS Section
    md_output.append("#### COMMANDS ####")
    commands = [
        {"name": "Initialize Project"},
        {"name": "Run Parsing"},
        {"name": "Generate Report"},
        {"name": "Export Data"}
    ]
    for command in commands:
        md_output.append(f"- [ ] {command['name']}")
    md_output.append("\n")

    # INSTRUCTIONS Section
    md_output.append("#### INSTRUCTIONS ####")
    instructions = [
        {"step": 1, "description": "Run the initial analysis on the source folder."},
        {"step": 2, "description": "Process the files and extract data summaries."},
        {"step": 3, "description": "Generate a final report in markdown format."}
    ]
    for instruction in instructions:
        md_output.append(f"{instruction['step']}. **{instruction['description']}**")
    md_output.append("\n")

    # ZEN Section
    md_output.append("#### ZEN ####")
    zen_philosophies = [
        "Simplicity is the ultimate sophistication.",
        "Code should be written for humans first, then for machines.",
        "Continuous improvement leads to mastery."
    ]
    for zen in zen_philosophies:
        md_output.append(f"- {zen}")
    md_output.append("\n")

    # ARTICLES Section
    md_output.append("#### ARTICLES ####")
    articles = {
        "Project": ["Introduction to Refactoring", "Best Practices for Code Analysis"],
        "Analysis": ["Understanding Code Complexity", "Improving Software Performance"]
    }
    for section, articles_list in articles.items():
        md_output.append(f"##### Articles on {section} #####")
        for article in articles_list:
            md_output.append(f"- {article}")
        md_output.append("\n")

    # Parsed Files Summary Section
    md_output.append("---\n")
    md_output.append("## Parsed Files Summary\n")
    for entry in data:
        if entry['status'] == 'Success':
            md_output.append(f"**File**: {entry['path']}")
            md_output.append(f"- Time Taken: {entry['time_taken']:.2f}s")
            if entry.get('data'):
                md_output.append(f"- Data Extracted: {entry['data']}")
        else:
            md_output.append(f"**Failed to process file**: {entry['path']}")
        md_output.append("\n")

    # JSON Representation Section
    md_output.append("---\n")
    md_output.append("#### JSON Representation ####")
    md_output.append("```json")
    md_output.append(json.dumps({
        "name": config['project'],
        "file": config['project_name'],
        "type": "Text/Markdown",
        "version": "1.0.0",
        "date": "2024-09-24",
        "author": "ScriptGPT",
        "goal": "Track project file parsing activities and output refactoring details.",
        "focus": "Refactoring, Analysis, Documentation",
        "tags": ["Refactoring", "Analysis", "Documentation"],
        "commands": commands,
        "instructions": instructions,
        "zen": zen_philosophies,
        "articles": articles,
        "parsed_files": [
            {
                "file_name": entry['path'],
                "time_taken": entry['time_taken'],
                "data_extracted": entry['data'] if entry['status'] == 'Success' else None
            } for entry in data
        ]
    }, indent=4))
    md_output.append("```")

    return "\n".join(md_output)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_directory = sys.argv[1]
        results = start_parsing(main_directory)
        for file_data in results:
            logging.info(f"Processed {file_data['path']}: {file_data['status']} in {file_data['time_taken']} seconds")
    else:
        logging.error("No directory provided.")
