import argparse
import json
import logging
import os
import sys
import tempfile
from io import BytesIO

import base64
import bz2
import csv
import gzip
import markdown2
import pytesseract
import py7zr
import yaml
import zipfile
from docx import Document
from PIL import Image, UnidentifiedImageError
from pdf2image import convert_from_path
from termcolor import colored
from tqdm import tqdm
from xml.etree import ElementTree as ET
import fnmatch
import tarfile
from datetime import datetime

# Function to check if a file or folder should be ignored
def matches_ignore_patterns(entry):
    for pattern in IGNORE_NAMES:
        if fnmatch.fnmatch(entry, pattern):
            return True
    return False

# Function to check if a file should be excluded based on config
def should_exclude_file(file_path):
    file_name = os.path.basename(file_path)
    _, file_ext = os.path.splitext(file_path)
    file_size = os.path.getsize(file_path)

    # Exclude small images
    if config['exclude']['small_images']['enabled'] and file_ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
        if file_size < config['exclude']['small_images']['size_threshold']:
            return True

    # Exclude all images
    if config['exclude']['exclude_images'] and file_ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
        return True

    # Exclude images at root level
    if config['exclude']['exclude_images_at_root'] and file_ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
        if os.path.dirname(file_path) == os.getcwd():
            return True

    # Exclude config and lock files
    if config['exclude']['exclude_config_files'] and file_ext.lower() in ['.json', '.yaml', '.yml', '.config']:
        return True
    if config['exclude']['exclude_lock_files'] and file_name in ['package-lock.json', 'yarn.lock']:
        return True

    return False

# Processing Functions
def process_directory(directory, logger, all_data):
    try:
        for entry in tqdm(os.listdir(directory), desc="Processing directory", unit="file", leave=False):
            if not matches_ignore_patterns(entry):
                process_entry(entry, directory, logger, all_data)
    except FileNotFoundError as e:
        logger.error(f"Directory not found: {directory}. Error: {e}")
        raise FileProcessingError(f"Directory not found: {directory}") from e

def process_entry(entry, directory, logger, all_data):
    if entry in ['.DS_Store', 'node_modules']:
        return

    entry_path = os.path.join(directory, entry)
    if should_exclude_file(entry_path):
        return
    if os.path.isdir(entry_path):
        if not matches_ignore_patterns(entry):
            process_directory(entry_path, logger, all_data)
    elif os.path.isfile(entry_path):
        if not matches_ignore_patterns(entry):
            process_file(entry_path, logger, all_data)
    else:
        logger.warning(f"Skipped unrecognized file type: {entry}")

def process_file(file_path, logger, all_data):
    try:
        data = parse_file(file_path, logger)
        if data:
            all_data.append(data)
        else:
            logger.warning(f"No data extracted from {file_path}")
    except InvalidFileTypeError as e:
        logger.error(f"Error processing file {file_path}: {e}")

# Custom Formatter with Color Coding
class ColoredFormatter(logging.Formatter):
    def __init__(self, config):
        super().__init__("%(levelname)s: %(message)s")
        self.config = config

    def format(self, record):
        levelname = record.levelname
        color = self.config['color_scheme'].get(levelname, 'white')
        levelname_color = colored(levelname, color)
        record.levelname = levelname_color
        return super(ColoredFormatter, self).format(record)

# Process archive
def process_archive(temp_extract_path, logger, all_data):
    for file in tqdm(os.listdir(temp_extract_path), desc="Processing files", unit="file", leave=False):
        file_path = os.path.join(temp_extract_path, file)
        if os.path.isdir(file_path):
            process_directory(file_path, logger, all_data)
        elif os.path.isfile(file_path):
            data = parse_file(file_path, logger)
            if data:
                all_data.append(data)

# Process single file
def process_single_file(file_path, temp_extract_path, logger, all_data):
    # Example for gz files, can be expanded for other formats
    if file_path.endswith('.gz'):
        extracted_file_path = os.path.join(temp_extract_path, os.path.basename(file_path).replace('.gz', ''))
        with gzip.open(file_path, 'rb') as gz_file:
            with open(extracted_file_path, 'wb') as out_file:
                out_file.write(gz_file.read())

        data = parse_file(extracted_file_path, logger)
        if data:
            all_data.append(data)

    # Similar logic for bz2 files
    elif file_path.endswith('.bz2'):
        extracted_file_path = os.path.join(temp_extract_path, os.path.basename(file_path).replace('.bz2', ''))
        with bz2.open(file_path, 'rb') as bz2_file:
            with open(extracted_file_path, 'wb') as out_file:
                out_file.write(bz2_file.read())

        data = parse_file(extracted_file_path, logger)
        if data:
            all_data.append(data)

    # Additional conditions can be added for other file formats

# Modified extract_and_parse_compressed function with tqdm progress bar
def extract_and_parse_compressed(folder_path, logger):
    all_data = []
    total_files_processed = 0
    source_file_size = 0
    source_name = None
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        source_file_size += os.path.getsize(file_path)
        source_name = filename

        if filename.endswith('.7z'):
            with py7zr.SevenZipFile(file_path, 'r') as archive:
                file_count = len(archive.getnames())
                total_files_processed += file_count
                with tempfile.TemporaryDirectory() as temp_extract_path:
                    archive.extractall(temp_extract_path)
                    process_archive(temp_extract_path, logger, all_data)

        elif filename.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_count = len(zip_ref.infolist())
                total_files_processed += file_count
                with tempfile.TemporaryDirectory() as temp_extract_path:
                    zip_ref.extractall(temp_extract_path)
                    process_archive(temp_extract_path, logger, all_data)

        elif filename.endswith('.tar'):
            with tarfile.open(file_path, 'r') as tar:
                file_count = len(tar.getnames())
                total_files_processed += file_count
                with tempfile.TemporaryDirectory() as temp_extract_path:
                    tar.extractall(temp_extract_path)
                    process_archive(temp_extract_path, logger, all_data)

        elif filename.endswith(('.gz', '.bz2')):
            with tempfile.TemporaryDirectory() as temp_extract_path:
                process_single_file(file_path, temp_extract_path, logger, all_data)

        else:
            # if direcstory recrusively process files
            if os.path.isdir(file_path):
                process_directory(file_path, logger, all_data)
            # if file process file
            elif os.path.isfile(file_path):
                data = parse_file(file_path, logger)
                if data:
                    all_data.append(data)
            else:
                logger.warning(f"Skipped unrecognized file type: {filename}")




    merged_data = validate_json_serializable(organize_data(all_data, source_name, logger),logger)


    # logger.info(f"Organized data from {len(all_data)} files.")
    # logger.debug(f"Data: {merged_data}")
    # output_file = os.path.join(folder_path, 'merged_data.json')
    output_file = os.path.join(OUTPUT_FOLDER, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{config['project_name']}.json")

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(merged_data, file, ensure_ascii=False, indent=4)

    output_file_size = os.path.getsize(output_file)
    size_difference = output_file_size - source_file_size
    logger.info(f"Merged data saved to {output_file} (Size: {output_file_size} bytes)")
    logger.info(f"Total files processed: {total_files_processed}")
    logger.info(f"Size difference from source: {size_difference} bytes")
    return merged_data

def validate_json_serializable(data, logger):
    if isinstance(data, dict):
        return {k: validate_json_serializable(v, logger) for k, v in data.items()}
    elif isinstance(data, list):
        return [validate_json_serializable(item, logger) for item in data]
    elif isinstance(data, Image.Image):
        return image_to_base64(data, logger)
    else:
        return data

def image_to_base64(image, logger):
    """Converts a PIL image to base64 string."""
    logger.info(f"Converting image to base64")
    buffered = BytesIO()
    logger.info(f"Buffering image")
    image.save(buffered, format="PNG")
    logger.info(f"Encoding image to base64")
    return base64.b64encode(buffered.getvalue()).decode()

# Parse file
def parse_file(file_path, logger):
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    _, file_extension = os.path.splitext(file_path)
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)


    if file_name == ['package-lock.json', 'package.json', 'yarn.lock', 'pnpm-lock.yaml', 'pnpm-lock.json']:
        return None

    # debug only
    logger.info(f"Parsing file: {file_name} (Size: {file_size} bytes)")

    parsed_data = None

    try:

        # Add PDF handling
        if file_extension.lower() == '.pdf':
            try:
                images = convert_from_path(file_path)
                pdf_data = {'text': [], 'images': []}
                for image in images:
                    pdf_data['text'].append(pytesseract.image_to_string(image))
                    pdf_data['images'].append(image)  # Store image object or convert to desired format
                parsed_data = pdf_data
            except Exception as e:
                logger.error(f"Error processing PDF file {file_path}: {e}")
                return None

        elif file_extension.lower() in ['.bmp', '.jpeg', '.png', '.gif', '.img', '.ico', '.svg', '.psd',  '.xcf']:
                try:
                    logger.info(f"Processing image file: {file_name}")
                    image = Image.open(file_path)
                    logger.info(f"Image opened: {file_name}")
                    image_base64 = image_to_base64(image, logger)
                    logger.info(f"Image converted to base64: {file_name}")
                    ocr_text = pytesseract.image_to_string(image)
                    logger.info(f"Image converted to text: {file_name}")
                    image_info = {
                        'format': image.format,
                        'size': image.size,
                        'mode': image.mode,
                        'ocr_text': ocr_text,
                        'image_base64': image_base64
                    }
                    parsed_data = image_info
                    logger.info(f"Image parsed with OCR: {file_name}")
                except UnidentifiedImageError:
                    logger.warning(f"Skipped non-image file: {file_name}")
                    return None

        elif file_extension.lower() in ['.json', '.babelrc', '.eslintrc']:
            logger.info(f"Processing JSON file: {file_name}")
            with open(file_path, 'r', encoding='utf-8') as file:
                parsed_data = json.load(file)

        elif file_extension.lower() in ['.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8') as file:
                parsed_data = yaml.safe_load(file)

        elif file_extension.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                parsed_data = file.read()

        elif file_extension.lower() in [ '.py', '.md', '.ts', '.js', '.html', '.php', '.xaml', '.editorconfig', '.gitignore', '.travis.yml'] or file_extension == '':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                parsed_data = markdown2.markdown(content) if file_extension.lower() == '.md' else content

        elif file_extension.lower() == '.csv':
            with open(file_path, newline='', encoding='utf-8') as file:
                parsed_data = list(csv.reader(file))

        elif file_extension.lower() == '.xml':
            # tree = ET.parse(file_path)
            # parsed_data = tree.getroot()
            parsed_data = file.read();

        elif file_extension.lower() in ['.doc', '.docx']:
            doc = Document(file_path)
            parsed_data = [paragraph.text for paragraph in doc.paragraphs]

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

    return {'data': parsed_data, 'file_name': file_name, 'file_size': file_size, "file_type": file_extension, "file_source": file_path} if parsed_data else None

# Determine data type
def determine_data_type(data, logger):


    if (isinstance(data, dict) and data.get('file_type') == '.json'):
         return 'json'

    if isinstance(data, dict):
        if 'text' in data and 'images' in data:
            return 'pdf'
        elif 'format' in data:
            return 'image'
        else:
            return 'json'
    elif isinstance(data, list):
        if all(isinstance(elem, list) for elem in data):
            return 'csv'
        else:
            return 'docx'
    elif isinstance(data, ET.Element):
        return 'xml'
    elif isinstance(data, str):
        return 'markdown' if '<p>' in data else 'text'
    else:
        return 'other'

def get_size(obj, seen=None):
    """Recursively finds size of objects in bytes"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def split_text_into_chunks(obj, max_bytes=1024, max_line_length=80):
    """Recursively splits strings in a nested object that exceed max_bytes or max_line_length."""
    if isinstance(obj, dict):
        return {k: split_text_into_chunks(v, max_bytes, max_line_length) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [split_text_into_chunks(elem, max_bytes, max_line_length) for elem in obj]
    elif isinstance(obj, str):
        if get_size(obj) > max_bytes or len(obj) > max_line_length:
            return split_string(obj, max_bytes, max_line_length)
        else:
            return obj
    else:
        return obj

def split_string(string, max_bytes, max_line_length):
    """Splits a string into chunks considering max_bytes and max_line_length."""
    chunks, current_chunk = [], ""
    for line in string.split('\n'):
        while len(line) > max_line_length:
            breakpoint = line.rfind(' ', 0, max_line_length)
            if breakpoint == -1:
                breakpoint = max_line_length
            current_chunk += line[:breakpoint] + '\n'
            if get_size(current_chunk) > max_bytes:
                chunks.append(current_chunk)
                current_chunk = ""
            line = line[breakpoint:].lstrip()
        current_chunk += line + '\n'
        if get_size(current_chunk) > max_bytes:
            chunks.append(current_chunk)
            current_chunk = ""
    if current_chunk:
        chunks.append(current_chunk)
    return {"chunks": chunks, "num_chunks": len(chunks), "chunk_lengths": [len(c) for c in chunks]}


def extract_source(file_source):
    if file_source is None:
        return None
    if isinstance(file_source, str):
        return file_source.split("temp", 1)[-1].split("src", 1)[-1]
    if isinstance(file_source, dict):
        return file_source['data']['file_name']
    return None

# Function to organize and classify different types of data from a list of data items
def organize_data(data_list, source_name, logger):

    # Initialize a dictionary to store organized data and metadata
    organized_data = {
        'metadata': {},
        'data': {
            'json': {}, 'csv': {}, 'xml': {}, 'text': {}, 'markdown': {},
            'docx': {}, 'image': {}, 'other': {}, 'pdf': {}
        }
    }

    # Variables for file naming and text processing
    key_counter = 1
    text_chunk_size_bytes = config['text_chunk_size_bytes']
    max_line_length = config['max_line_length']
    current_compressed_file = None
    # Iterate through each data item in the list
    for data_item in data_list:

        # Replace periods in file names with underscores and handle empty filenames
        logger.debug(f"Processing file name {data_item['file_name']}")
        file_name = data_item['file_name'].replace('.', '_')
        if not file_name:
            file_name = f"file_{key_counter}"
            key_counter += 1

        # Determine file extension
        file_extension = "";
        try:
            file_extension = os.path.splitext(data_item['file_name'])[1];
            # if file_extension == '':
                # file_name = f"{file_name}.txt"
        except Exception as e:
            logger.error(f"Error processing file name {file_name}: {e}")

        # Determine file source
        file_source = data_item['file_source']

        # if is compressed file then set current_compressed_file to file_name else set to None
        if file_extension in ['.7z', '.zip', '.tar', '.gz', '.bz2']:
            current_compressed_file = file_name
        else:
            current_compressed_file = None

        # Determine the type of data (e.g., pdf, image, json)
        logger.debug(f"Determining data type for file {file_name} with extension {file_extension}")

        if (file_extension==".json"):
            data_type = 'json'
        elif (file_extension==".md"):
            data_type = 'markdown'
        else:
            data_type = determine_data_type(data_item['data'], logger)

        logger.debug(   f"Data type: {data_type}")
        # Ensure unique data keys for storage
        data_key = file_name if file_name not in organized_data['data'][data_type] else f"{file_name}_{key_counter}"

        logger.debug(f"Organizing data from file {data_item['file_name']} under key {data_key}")
        logger.debug(f"Data type: {data_type}")
        # Store metadata for each data item
        organized_data['metadata'][data_key] = {
            'type': data_type,
            'description': f"Data item from {data_item['file_name']}",
            'file_name': data_item['file_name'],
            'file_size': data_item['file_size'],
            'source': extract_source(file_source)
        }

        # Handle PDF data specifically
        if data_type == 'pdf':
            pdf_data = data_item['data']
            organized_data['data']['pdf'][data_key] = {
                'text': pdf_data['text'],
                'images': pdf_data['images']
            }
            logger.debug(f"Organized PDF data from file {data_item['file_name']} under key {data_key}")

        # Handle image data specifically
        if data_type == 'image':
            image_data = data_item['data']
            organized_data['data']['image'][data_key] = {
                'metadata': {
                    'format': image_data['format'],
                    'size': image_data['size'],
                    'mode': image_data['mode']
                },
                'ocr_text': image_data['ocr_text']
            }
            logger.debug(f"Organized image data from file {data_item['file_name']} under key {data_key}")

        # Store data directly for certain types like CSV, XML, and DOCX
        if data_type in [ 'csv', 'xml', 'docx']:
            organized_data['data'][data_type][data_key] = data_item['data']

        # handle JSON data specifically
        if data_type in ['json']:
            # measure size of JSON data
            json_size = len(json.dumps(data_item['data'], ensure_ascii=False, indent=4).encode('utf-8'))
            logger.debug(f"Size of JSON data: {json_size} bytes")
            # if JSON data is larger than config['json_chunk_size_bytes'] or config['text_chunk_size_bytes']
            if json_size > config['json_chunk_size_bytes'] or json_size > text_chunk_size_bytes:

                temp_json = data_item['data'] # json.dumps(data_item['data'], ensure_ascii=False, indent=4)
                chunks = [];
                for value in temp_json:
                    for key in value:
                        # logging.debug(f"Key: {key}")
                        chunks.append(
                            split_text_into_chunks(value[key], text_chunk_size_bytes, max_line_length)
                        )

                for idx, chunk in enumerate(chunks):
                    chunk_key = f"{data_key}_chunk_{idx}"

                    try:
                        organized_data['metadata'][data_key][chunk_key] = {
                            # 'type': 'json_chunk',
                            # 'description': f"Chunk {idx} of {data_key}",
                            'file_name': data_item['file_name'],
                            # 'file_size': len(chunk.encode('utf-8')),
                            # 'source': extract_source(data_item['file_source'])
                        }
                        if data_key not in organized_data['data'][data_type]:
                            organized_data['data'][data_type][data_key] = {}
                            organized_data['data'][data_type][data_key][chunk_key] = {}
                        organized_data['data'][data_type][data_key][chunk_key] = {
                            'data': '',
                            'metadata': {
                                # 'type': 'json_chunk',
                                # 'description': f"Chunk {idx} of {data_key}",
                                'file_name': data_item['file_name'],
                                # 'file_size': len(chunk.encode('utf-8')),
                                # 'source': extract_source(data_item['file_source']),
                                # 'chunk_size': len(chunk.encode('utf-8')),
                                'chunk_number': idx,
                                # 'total_chunks': len(chunks)
                            }
                        }

                        try:
                            organized_data['data'][data_type][data_key][chunk_key]['data'] = json.loads(chunk)
                        except Exception as e:
                            organized_data['data'][data_type][data_key][chunk_key]['data'] = (chunk)
                            # logger.warning(f"Error parsing JSON chunk {idx} from {chunk}: {e} falling back to text")
                        # Store metadata for each chunk

                    except Exception as e:
                        logger.error(f"Error parsing JSON chunk {idx} from {chunk}: {e}")

                    logger.debug(f"Added JSON chunk {idx} to organized data")
            else:
                organized_data['data'][data_type][data_key] = {
                    'data': data_item['data'],
                    'metadata': {
                        # 'type': 'json',
                        # 'description': f"JSON data from {data_item['file_name']}",
                        'file_name': data_item['file_name'],
                        'file_size': json_size,
                    }
                }
        #
        #
        # Handle text-based data including HTML, text, markdown, PDF, and others
        #
        #
        if data_type in ['html', 'text', 'markdown', 'pdf', 'image', 'other']:
            text_content = data_item['data']
            # Special handling for image and JSON data
            if data_type == 'image':
                text_content = image_data['ocr_text']
            elif data_type == 'json':
                text_content = json.dumps(data_item['data'], ensure_ascii=False, indent=4)
                logger.debug(f"JSON data converted to text: {text_content}")

            # Split text content into chunks if it exceeds size or line length limits
            if len(text_content.encode('utf-8')) > text_chunk_size_bytes or any(len(line) > max_line_length for line in text_content.split('\n')):
                chunks = split_text_into_chunks(text_content, text_chunk_size_bytes, max_line_length)
                for idx, chunk in enumerate(chunks):
                    chunk_key = f"{data_key}_chunk_{idx}"

                    # if data_key not in organized_data['data'][data_type]:
                    organized_data['data'][data_type][data_key] = {}
                    organized_data['data'][data_type][data_key][chunk_key] = {}
                    organized_data['data'][data_type][data_key][chunk_key] = chunk
                    organized_data['metadata'][chunk_key] = {
                        'type': 'text_chunk',
                        'description': f"Chunk {idx} of {data_key}",
                        'file_name': data_item['file_name'],
                        'file_size': len(chunk.encode('utf-8')),
                        'source': extract_source(data_item['file_source'])
                    }
            else:
                organized_data['data'][data_type][data_key] = {}
                organized_data['data'][data_type][data_key] = {
                    'content': text_content,
                    'metadata': {
                        'type': data_type,
                        'description': f"{data_type} data from {data_item['file_name']}",
                        'file_name': data_item['file_name'],
                        'file_size': len(text_content.encode('utf-8')),
                        'source': extract_source(data_item['file_source'])
                    }
                }

    # Log the number of organized data files
    logger.debug(f"Organized data from {len(data_list)} files.")

    # take the organized data and deep nest loop through the keys and values to ensure that none of the strings are larger than config['max_line_length'] and if they are rewrite the key into an object with chunks of config['max_line_length']



    def deep_nest_data(organized_data, max_line_length):
        def split_text_into_chunks(text, max_line_length):
            chunks = []
            current_chunk = ""
            lines = text.split('\n')
            for line in lines:
                if len(current_chunk) + len(line) <= max_line_length:
                    current_chunk += line + '\n'
                else:
                    chunks.append(current_chunk)
                    current_chunk = line + '\n'
            if current_chunk:
                chunks.append(current_chunk)
            return chunks

        def process_data(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > max_line_length:
                        chunks = split_text_into_chunks(value, max_line_length)
                        data[key] = {
                            'type': 'text_chunk',
                            'chunks': chunks
                        }
                    else:
                        process_data(value)
            elif isinstance(data, list):
                for i in range(len(data)):
                    process_data(data[i])
            return data

        processed_data = process_data(organized_data)
        return processed_data

    # Return the organized data
    return deep_nest_data(organized_data, config['max_line_length'])



# Process data for ScriptGPT
def process_for_scriptgpt(processing_data, logger):
    logger.debug("Starting processing for ScriptGPT")

    # Initialize containers for organized data
    processed_data = {
        'json': {},
        'csv': {},
        'xml': {},
        'text': {},
        'markdown': {},
        'docx': {},
        'image': {},
        'pdf': {}
    }

    try:
        for data_type, data_items in processing_data['data'].items():
            for data_key, data_item in data_items.items():
                metadata = processing_data['metadata'].get(data_key, {})
                if data_type == 'image':
                    # Process OCR text for images
                    processed_data['image'][data_key] = {
                        'ocr_text': data_item['ocr_text'],
                        'metadata': metadata
                    }
                elif data_type == 'pdf':
                    # Process text and images from PDF
                    processed_data['pdf'][data_key] = {
                        'text': data_item['text'],
                        'images': data_item['images'],
                        'metadata': metadata
                    }
                else:
                    # Other data types
                    processed_data[data_type][data_key] = {
                        'content': data_item,
                        'metadata': metadata
                    }

    except Exception as e:
        logger.error(f"An error occurred in process_for_scriptgpt: {e}")

    logger.info("Data processing for ScriptGPT completed")
    return processed_data

# Output data
def output_data(data, folder_path, logger):
    output_file = os.path.join(folder_path, 'organized_data.json')
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4, sort_keys=True)

    logger.info(colored(f"Data organized and saved to {output_file}", "green"))

# Clear console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Main function updated with improved error handling
def main():
    # clear log
    if os.path.exists(config['log_file_path']):
        os.remove(config['log_file_path'])

    clear_console()

    args = parse_args()
    logger = setup_logger(config, debug_mode=True)

    src_folder_path = os.path.join(os.getcwd(), SRC_FOLDER)
    output_folder_path = os.path.join(os.getcwd(), OUTPUT_FOLDER)

    try:
        if not os.path.exists(src_folder_path):
            raise FileProcessingError(f"Source directory not found: {src_folder_path}")

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        merged_data = extract_and_parse_compressed(src_folder_path, logger)
        # organized_data = process_for_scriptgpt(merged_data, logger)
        # output_data(organized_data, output_folder_path, logger)

        logger.info("Script execution completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
