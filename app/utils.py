from pathlib import Path

import requests


def save_image_locally(url: str, product_title: str) -> str:
    response = requests.get(url, stream=True)
    Path("images").mkdir(parents=True, exist_ok=True)
    local_path = f"images/{product_title.replace(' ', '_')}.jpg"
    with open(local_path, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
    return local_path
