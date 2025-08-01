
import argparse
from rich.console import Console
from rich.table import Table
import logger


#Formats
formatsData = [
    "PDF",
    "MD",
    "DOCX",
    "JSON",
    "CSV",
    "XML",
    "YAML"
]

formatsOCR = [
    "BMP",
    "JPEG",
    "PNG",
    "GIF",
    "TIFF",
    "WEBP"
]

# Create a console object
console = Console()

from typing import Dict, Any

def initialize(CONFIG: Dict[str, Any]):
    # Initialize the logger
    log = logger.setup_logger(CONFIG, CONFIG['log_level']=='DEBUG')
    args = parse_args()

    formatsDataString = ", ".join(formatsData) + ", Image Formats";
    formatsOCRString = ", ".join(formatsOCR);

    # Create a table
    try:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Feature", style="dim", width=20)
        table.add_column("Description", width=60)
        table.add_column("File Support", justify="left")

        # Add rows to the table with the script's features and file support
        table.add_row(
            "Data Extraction",
            "Text and image files are extracted from files OCR'd, Organized, and stored in a structured format.",
            formatsDataString
        )
        table.add_row(
            "OCR Capabilities",
            "Performs Optical Character Recognition on image files to extract text.",
            formatsOCRString
        )
        table.add_row(
            "Data Organization",
            "Chunks and Organizes extracted data into a structured format for easy access and processing.",
            "MD + JSON"
        )
        table.add_row(
            "Progress Logging",
            "\n",
            "log.txt"
        )
        table.add_row(
            "Configuration",
            "",
            "./gpt.knowledge.compiler.json"
        )

        # Print a friendly starting message
        console.print("Starting [bold green]gpt-knowledge-compiler[/bold green]...", "\n")

        console.print(table)

        return console,args
    except ModuleNotFoundError as e:
        print(f"Module not found: {e}. Please install the 'rich' library to use this feature.")

# Command Line Arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Enhanced Python Script with Logging and Configuration')

    # Adding the necessary arguments
    parser.add_argument('--url', type=str, required=True, help='The URL to process')
    parser.add_argument('--match', type=str, required=True, help='The match pattern for URLs')
    parser.add_argument('--project', type=str, required=True, help='The project name')
    # parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    return parser.parse_args()

# Assuming that this file is executed directly
if __name__ == "__main__":
    CONFIG = {}
    console, args = initialize(CONFIG)