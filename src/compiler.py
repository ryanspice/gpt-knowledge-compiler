import os
import logger

from config import CONFIG
from parser import start_parsing

import startup

# Custom Exceptions
class FileProcessingError(Exception):
    pass

class InvalidFileTypeError(Exception):
    pass

# Clear console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    pass

# Initialize
def initialize():
    clear_console()
    return startup.initialize(CONFIG)

# Main`
def main():
    console,args = initialize()
    logger.debug("Starting main function.")
    logger.info("Logging Level:");
    logger.info(f"  {CONFIG['log_level']}")

    # Print CONFIG values
    logger.debug("Configuration Values:")

    for key, value in CONFIG.items():
        # if inside object 'projects' print each project
        if key == 'projects':
            logger.info("Projects:")
            for project in value:
                logger.info(f"  {project}")
        else:
            logger.debug(f"{key}: {value}")

    # logger.info("The compiler is running...")
    # logger.debug("Building file list...")

    # Get the current working directory, adjusted for project structure.
    directory = os.path.join(CONFIG["src_folder"])
    logger.debug(f"Processing in directory: {directory}")

    # Start the file processing
    files_processed = start_parsing(CONFIG,directory)
    console.print(f"Total files processed: {len(files_processed)}")
    pass


if __name__ == '__main__':
    main(CONFIG)
