import inspect
import logging
import os


def get_logger_name(module_file: str):
    """Gets the file name without the full path using a platform-agnostic approach.

    Args:
        module_file: The full path to the module file.

    Returns:
        The file name without the full path.
    """

    head, tail = os.path.split(module_file)
    return tail or os.path.basename(head)  # Handle cases where head is empty


def get_logger(level: int = logging.INFO):
    caller_frame = inspect.stack()[1]  # Get the frame of the caller
    caller_filename = caller_frame.filename  # Extract the filename
    logger_name = get_logger_name(caller_filename)
    logger = logging.getLogger(logger_name)

    # Add handlers (e.g., console, file)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] - %(levelname)s - %(name)s: %(message)s",
        datefmt="%m-%d-%Y %H:%M:%S",
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(level)

    return logger
