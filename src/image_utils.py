"""Image utilities for homework analysis with Claude Vision."""
import base64
from typing import Optional
from pathlib import Path


def encode_image_to_base64(image_path: str) -> Optional[str]:
    """
    Encode an image file to base64 string.

    Args:
        image_path: Path to image file

    Returns:
        Base64 encoded string or None if error
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def encode_image_bytes_to_base64(image_bytes: bytes) -> Optional[str]:
    """
    Encode image bytes to base64 string.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Base64 encoded string or None if error
    """
    try:
        return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image bytes: {e}")
        return None


def get_image_media_type(file_name: str) -> str:
    """
    Determine media type from file extension.

    Args:
        file_name: Name of the image file

    Returns:
        Media type string (e.g., 'image/jpeg', 'image/png')
    """
    extension = Path(file_name).suffix.lower()

    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }

    return media_types.get(extension, 'image/jpeg')
