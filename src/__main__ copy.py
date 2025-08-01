import os
import sys
import json

from rich.console import Console

from config import *

import startup
import logger
import gpt_crawler
import parse_arguments

import process_directory
import json

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

# Load configuration
CONFIG = load_config()
SRC_FOLDER = CONFIG['src_folder']
OUTPUT_FOLDER = CONFIG['output_folder']


def main():

	clear_console()
	log = logger.setup_logger(CONFIG, True)
	startup.info(CONFIG)
	args = parse_arguments.parse_arguments(CONFIG)

	src_folder_path = os.path.join(os.getcwd(), SRC_FOLDER)
	output_folder_path = os.path.join(os.getcwd(), OUTPUT_FOLDER)

	files_to_process = process_directory.process_directory(src_folder_path, logger, [])

	# print files_to_process nearly with rich
	console = Console()

	# console.print("Files to process: ")

	# Get number of files to process
	num_files = len(files_to_process)
	log.info(f"Files to process: {num_files}")
	# log.info(f"{json.dumps(files_to_process, indent=4)}")

	# gpt_crawler.main()

if __name__ == "__main__":
	main()