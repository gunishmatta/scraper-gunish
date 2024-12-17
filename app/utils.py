import re
from pathlib import Path
import requests

def sanitize_filename(name: str) -> str:
    """Remove invalid file path characters and limit filename length."""
    sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
    sanitized = re.sub(r'\s+', "_", sanitized)
    return sanitized[:100]

def save_image_locally(url: str, product_title: str) -> str:
    """Download image from URL and save it locally with a sanitized filename."""
    response = requests.get(url, stream=True)
    Path("images").mkdir(parents=True, exist_ok=True)
    safe_title = sanitize_filename(product_title)
    local_path = f"images/{safe_title}.jpg"
    with open(local_path, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
    return local_path
