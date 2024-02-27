import inspect
import logging
import os

from coloredlogs import ColoredFormatter


def get_logger_name(module_file: str):
    head, tail = os.path.split(module_file)
    return tail or os.path.basename(head)  # Handle cases where head is empty


def get_logger(level: int = logging.INFO):
    caller_frame = inspect.stack()[1]  # Get the frame of the caller
    caller_filename = caller_frame.filename  # Extract the filename
    logger_name = get_logger_name(caller_filename)
    logger = logging.getLogger(logger_name)

    # Add handlers (e.g., console, file)
    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        # "[%(asctime)s] - %(levelname)s - %(name)s: %(message)s",
        "[%(asctime)s] %(message)s",
        datefmt="%m-%d-%Y %H:%M:%S.%f",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger
