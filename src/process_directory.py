import os
import fnmatch
from rich.progress import Progress

# Assuming the config module and IGNORE_NAMES are defined elsewhere
from config import IGNORE_NAMES

# Assuming logger setup and process_entry function are defined elsewhere

# Custom Exceptions
class FileProcessingError(Exception):
    pass

# Function to check if a file or folder should be ignored
def matches_ignore_patterns(entry):
    for pattern in IGNORE_NAMES:
        if fnmatch.fnmatch(entry, pattern):
            return True
    return False

def process_directory(directory, logger, all_data):
    try:
        file_list = []
        # Initialize Progress object
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning directory...", total=len(os.listdir(directory)))

            for entry in os.scandir(directory):
                # Update progress bar
                progress.update(task, advance=1)
                if not matches_ignore_patterns(entry.name):
                    if entry.is_file():
                        file_list.append(entry.path)
                    elif entry.is_dir():
                        # Recursively process directories
                        file_list.extend(process_directory(entry.path, logger, all_data))
        return file_list
    except FileNotFoundError as e:
        logger.error(f"Directory not found: {directory}. Error: {e}")
        raise FileProcessingError(f"Directory not found: {directory}") from e
