import os
import json
import logging
from typing import Dict, Any
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from logging.handlers import RotatingFileHandler

def setup_logger(config: Dict[str, Any], debug_mode: bool) -> logging.Logger:
    logger = logging.getLogger(__name__)

    # Avoid duplicate handlers by clearing existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    setup_log_level(logger, config, debug_mode)
    setup_handlers(logger, config, debug_mode)

    # Ensure logs propagate correctly
    logger.propagate = False
    return logger

def setup_log_level(logger: logging.Logger, config: Dict[str, Any], debug_mode: bool) -> None:
    log_level = logging.DEBUG if debug_mode else config['log_level']
    logger.setLevel(log_level)

def setup_handlers(logger: logging.Logger, config: Dict[str, Any], debug_mode: bool) -> None:
    setup_console_handler(logger, config, debug_mode)
    if config.get('log_to_file', False):
        setup_file_handler(logger, config, debug_mode)

def setup_console_handler(logger: logging.Logger, config: Dict[str, Any], debug_mode: bool) -> None:
    custom_theme = Theme(config.get("theme", {"info": "dim cyan", "warning": "magenta", "error": "bold red"}))
    console = Console(theme=custom_theme)
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=config.get('rich_tracebacks', True),
        tracebacks_show_locals=config.get('tracebacks_show_locals', False),
        show_time=config.get('show_time', True),
        markup=config.get('markup', True)
    )
    rich_handler.setLevel(config.get('console_log_level', logging.DEBUG if debug_mode else config['log_level']))

    # Ensure consistent formatting
    formatter = logging.Formatter(config.get('console_format', "%(message)s"))
    rich_handler.setFormatter(formatter)

    logger.addHandler(rich_handler)

def setup_file_handler(logger: logging.Logger, config: Dict[str, Any], debug_mode: bool) -> None:
    file_log_level = config.get('file_log_level', logging.DEBUG if debug_mode else config['log_level'])
    fh = RotatingFileHandler(
        config['log_file_path'],
        maxBytes=config.get('log_file_max_size', 10*1024*1024),
        backupCount=config.get('log_file_backup_count', 5)
    )
    fh.setLevel(file_log_level)
    set_file_formatter(fh, config)
    logger.addHandler(fh)

def set_file_formatter(fh: RotatingFileHandler, config: Dict[str, Any]) -> None:
    if config.get('structured_logging', False):
        fh.setFormatter(logging.Formatter('%(message)s'))
        fh.addFilter(lambda record: setattr(record, "message", json.dumps(record.__dict__)))
    else:
        file_format = config.get('file_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(logging.Formatter(file_format))

def clear_log_file(log_file_path: str) -> None:
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

def debug(message: str) -> None:
    logger.debug(message)

def info(message: str) -> None:
    logger.info(message)

def warning(message: str) -> None:
    logger.warning(message)

def error(message: str) -> None:
    logger.error(message)

def critical(message: str) -> None:
    logger.critical(message)

# Example usage:
config = {
    'log_file_path': 'log.txt',
    'log_level': logging.INFO,
    'log_to_file': True,
    'file_log_level': logging.ERROR,
    'theme': {"info": "dim cyan", "warning": "magenta", "error": "bold red"},
    'rich_tracebacks': True,
    'tracebacks_show_locals': False,
    'console_format': "%(message)s",
    'show_time': True,
    'markup': True,
    'console_log_level': logging.INFO,
}
debug_mode = False
logger = setup_logger(config, debug_mode)
