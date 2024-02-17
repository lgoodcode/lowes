from os import mkdir, path
from urllib.parse import urljoin

from constants import LOWES_URL, OUTPUT_DIR


def create_directory(directory_path: str):
    """Create a directory if it does not exist in the /output directory."""

    if not directory_path.startswith(OUTPUT_DIR):
        directory_path = path.join(OUTPUT_DIR, directory_path)
    if not path.exists(directory_path):
        mkdir(directory_path)
        print(f"Directory created successfully: {directory_path}")


def get_output_path(file_path: str) -> str:
    """Return the path to a file in the /output directory."""

    create_directory(OUTPUT_DIR)  # Ensure output directory exists
    return path.join(OUTPUT_DIR, file_path)


def get_full_lowes_url(relative_url: str) -> str:
    """Return the full URL to a page on lowes.com."""

    return urljoin(LOWES_URL, relative_url)
