import argparse
import json
from rich.console import Console
from rich.table import Table

def parse_arguments(CONFIG):
    # Initialize Rich console
    console = Console()

    # Load the configuration from a properly formatted JSON file
    try:
        with open("gpt.knowledge.compiler.json") as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        console.print("[bold red]Error:[/] gpt.knowledge.compiler.json file not found.", style="bold red")
        exit(1)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/] Invalid JSON format in gpt.knowledge.compiler.json.", style="bold red")
        exit(1)

    parser = argparse.ArgumentParser(description="Run gpt-crawler with optional configuration via command line or interactive prompt.")
    parser.add_argument("--project", help="The Project Name", type=str, default=config_data.get("project"))
    parser.add_argument("--url", help="The URL to crawl", type=str, default=config_data.get("url"))
    parser.add_argument("--match", help="The match pattern for URLs to crawl", type=str, default=config_data.get("match"))
    parser.add_argument("--skip-install", help="Skip checking and installing gpt-crawler", action="store_true", default=config_data.get("skipInstall", False))
    args = parser.parse_args()

    # dump args with rich but not table
    # console.print(args)

    # # Output parsed arguments using a table
    # table = Table(show_header=True, header_style="bold green")
    # table.add_column("Argument", style="dim")
    # table.add_column("Value")

    # # Add rows to the table for each argument
    # for arg, value in vars(args).items():
    #     table.add_row(arg, str(value))

    # console.print(table)

    return args

if __name__ == "__main__":
    parse_arguments()
