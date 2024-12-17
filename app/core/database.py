import json
from pathlib import Path

from app.core.interfaces import AbstractDatabase
from app.models import Product


class JsonDatabase(AbstractDatabase):
    def __init__(self, file_path: str = "data/products.json"):
        self.file_path = file_path
        Path("data").mkdir(parents=True, exist_ok=True)

    def save_product(self, product: Product):
        products = self._load_data()
        products.append(product.model_dump(exclude={'image_url'}))
        with open(self.file_path, "w") as f:
            json.dump(products, f, indent=4)

    def _load_data(self):
        if Path(self.file_path).exists():
            with open(self.file_path, "r") as f:
                return json.load(f)
        return []
