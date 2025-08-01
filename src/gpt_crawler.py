import argparse
import logging
import git  # GitPython
from invoke import Context  # Import Context
import json
import os

import parse_arguments

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration cache file path
cache_file_path = '.gpt_crawler_cache.json'

# Directory for gpt-crawler
gpt_crawler_dir = '.cache/gpt-crawler'
get_output_dir = '../../output/'

# Check if cache file exists
if os.path.exists(cache_file_path):
    with open(cache_file_path, 'r') as file:
        cache_data = json.load(file)
else:
    cache_data = {}

# Get list of files in output directoryq
current_output_files = os.listdir(get_output_dir)



# Run command
def run_command(command, cwd=None):
    context = Context()  # Create a Context instance
    if cwd:
        with context.cd(cwd):  # Use context.cd to change directory if cwd is specified
            result = context.run(command, hide=False, warn=True)  # Use context.run to execute the command
    else:
        result = context.run(command, hide=False, warn=True)
    if result.ok:
        logging.info("Command executed successfully.")
    else:
        logging.error(f"Command execution failed: {result.stderr}")

# Clone gpt-crawler
def clone_gpt_crawler():
    logging.info("Checking if gpt-crawler is already cloned...")
    if os.path.exists(os.path.join(gpt_crawler_dir, '.git')):
        logging.info("gpt-crawler is already cloned.")
        return
    else:
        logging.info("Cloning gpt-crawler...")
        try:
            git.Repo.clone_from('https://github.com/BuilderIO/gpt-crawler', gpt_crawler_dir)
            logging.info("gpt-crawler cloned successfully.")
        except Exception as e:
            logging.error(f"Failed to clone gpt-crawler: {e}")
            exit(1)

# Install gpt-crawler dependencies with
def install_gpt_crawler_dependencies():
    if os.path.exists(os.path.join(gpt_crawler_dir, 'node_modules')):
        logging.info("Dependencies are already installed.")
        return
    else:
        logging.info("Installing gpt-crawler dependencies...")
        run_command('pnpm install', cwd=gpt_crawler_dir)  # Corrected to properly handle command result

def generate_unique_filename(base_dir, base_name, extension):
    count = 0
    if base_name.endswith('.'):
        base_name = base_name[:-1]

    while True:
        unique_name = f"{base_name}{'-' + str(count) if count > 0 else ''}.{extension}"
        full_path = os.path.join(base_dir, unique_name)

        if not os.path.exists(full_path):
            return full_path

        count += 1


def get_unique_file_name(base_path, base_name, extension):
    """
    Generates a unique file name by appending a number before the extension.
    Returns the unique file path as a string without creating the file.
    """
    directory = os.path.dirname(base_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    count = 1  # Start with 1
    while True:
        # Construct the file name with number before the extension
        file_name = f"{base_name}-{count}.{extension}"
        file_path = os.path.join(base_path, file_name)

        # Check if the file already exists
        if not os.path.exists(file_path):
            # If it doesn't exist, return the unique file path
            return file_path

        count += 1  # Increment the count and try again
def create_update_config_js(url, match, project='', maxPagesToCrawl=5000):
    base_name = f"{project + '-' if project else ''}{url.replace('https://', '').replace('/', '.')}"
    outputFileName = generate_unique_filename(get_output_dir, base_name, 'json')
    config_js_content = f"""
import {{ Config }} from "./src/config";

let url = '{url}';
let match = '{match}';
let maxPagesToCrawl = {maxPagesToCrawl};

export const defaultConfig: Config = {{
  url,
  match,
  maxPagesToCrawl,
  outputFileName: '{get_unique_file_name(get_output_dir, base_name, 'json')}'
}};
"""
    config_file_path = os.path.join(gpt_crawler_dir, 'config.ts')
    with open(config_file_path, 'w') as config_file:
        config_file.write(config_js_content)
    logging.info(f"config.js has been updated. Output file: {outputFileName}")

def main():
    args = parse_arguments.parse_arguments()

    if not args.skip_install:
        clone_gpt_crawler()
        install_gpt_crawler_dependencies()

    if args.url and args.match:
        create_update_config_js(args.url, args.match, args.project)
    else:
        logging.error("URL and match pattern are required.")
        exit(1)

    logging.info("Running gpt-crawler...")
    run_command('npm run start', cwd=gpt_crawler_dir)

if __name__ == '__main__':
    main()
