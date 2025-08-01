import json
import logging

# Helper function to determine data type
def determine_data_type(data):
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


# Helper function to split text into chunks
def split_text_into_chunks(text, max_bytes, max_line_length):
    """
    Splits the text into chunks, considering maximum byte size and line length.
    Refactored to optimize performance and readability.
    """
    def add_chunk(chunks_list, current_chunk_lines):
        chunks_list.append('\n'.join(current_chunk_lines))

    chunks = []
    current_chunk_lines = []
    current_byte_size = 0

    lines = text.split('\n')
    for line in lines:
        sub_lines = [line[i:i + max_line_length] for i in range(0, len(line), max_line_length)]

        for sub_line in sub_lines:
            sub_line_bytes = len(sub_line.encode('utf-8'))
            if current_byte_size + sub_line_bytes > max_bytes:
                add_chunk(chunks, current_chunk_lines)
                current_chunk_lines = [sub_line]
                current_byte_size = sub_line_bytes
            else:
                current_chunk_lines.append(sub_line)
                current_byte_size += sub_line_bytes

    if current_chunk_lines:
        add_chunk(chunks, current_chunk_lines)

    return chunks


# Helper function to organize data by type
def organize_data_by_type(data_item, data_key, organized_data, config, logger):
    data_type = determine_data_type(data_item['data'])
    organized_data['metadata'][data_key] = {
        'type': data_type,
        'description': f"Data item from {data_item['file_name']}",
        'file_name': data_item['file_name'],
        'file_size': data_item['file_size'],
        'source_zip': data_item['zip_file_name']
    }

    if data_type == 'pdf':
        organize_pdf_data(data_item, data_key, organized_data)
    elif data_type == 'image':
        organize_image_data(data_item, data_key, organized_data)
    elif data_type in ['json', 'csv', 'xml', 'docx']:
        organized_data['data'][data_type][data_key] = data_item['data']
    elif data_type in ['html', 'text', 'markdown', 'pdf', 'image', 'other']:
        organize_text_data(data_item, data_key, organized_data, config, logger)

def organize_pdf_data(data_item, data_key, organized_data):
    pdf_data = data_item['data']
    organized_data['data']['pdf'][data_key] = {
        'text': pdf_data['text'],
        'images': pdf_data['images']
    }

def organize_image_data(data_item, data_key, organized_data):
    image_data = data_item['data']
    organized_data['data']['image'][data_key] = {
        'metadata': {
            'format': image_data['format'],
            'size': image_data['size'],
            'mode': image_data['mode']
        },
        'ocr_text': image_data['ocr_text']
    }

def organize_text_data(data_item, data_key, organized_data, config, logger):
    text_content = data_item['data']
    text_chunk_size_bytes = config['text_chunk_size_bytes'] * 0.1
    max_line_length = config['max_line_length']

    if len(text_content.encode('utf-8')) > text_chunk_size_bytes or any(len(line) > max_line_length for line in text_content.split('\n')):
        chunks = split_text_into_chunks(text_content, text_chunk_size_bytes, max_line_length)
        for idx, chunk in enumerate(chunks):
            chunk_key = f"{data_key}_chunk_{idx}"
            organized_data['data'][data_item['data_type']][chunk_key] = chunk
            # Add metadata for the chunk

            organized_data['metadata'][chunk_key] = {
                'type': data_item['data_type'],
                'description': f"Data item from {data_item['file_name']}",
                'file_name': data_item['file_name'],
                'file_size': data_item['file_size'],
                'source_zip': data_item['zip_file_name'],
                'chunk': idx
            }

    else:
        organized_data['data'][data_item['data_type']][data_key] = text_content

# Main function to organize data
def organize_data(data_list, zip_file_name, logger):
    logger = logging.getLogger(__name__)
    organized_data = {
        'metadata': {},
        'data': {
            'json': {}, 'csv': {}, 'xml': {}, 'text': {}, 'markdown': {}, 'docx': {}, 'image': {}, 'other': {}, 'pdf': {}
        }
    }
    key_counter = 1
    config = {'text_chunk_size_bytes': 1024, 'max_line_length': 80}  # Placeholder for config

    for data_item in data_list:
        if 'data_type' not in data_item:
            logger.error(f"Missing 'data_type' in data_item: {data_item}")
            continue  # Skip this item and continue with the next one

        file_name = data_item['file_name'].replace('.', '_') or f"file_{key_counter}"
        key_counter += 1

        data_key = file_name if file_name not in organized_data['data'][data_item['data_type']] else f"{file_name}_{key_counter}"
        organize_data_by_type(data_item, data_key, organized_data, config, logger)

    logger.debug(f"Organized data from {len(data_list)} files.")
    return organized_data


# Example usage
if __name__ == "__main__":
    # Example data_list and zip_file_name
    data_list = [{'file_name': 'example.pdf', 'data': {}, 'file_size': 1024}]
    zip_file_name = 'archive.zip'
    organized_data = organize_data(data_list, zip_file_name, logging.getLogger(__name__))
    print(organized_data)
