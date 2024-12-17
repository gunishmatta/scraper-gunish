import json
from app.models import Product
from pathlib import Path

class Database:
    def __init__(self, file_path: str = "data/products.json"):
        self.file_path = file_path
        Path("data").mkdir(parents=True, exist_ok=True)

    def save_product(self, product: Product):
        pass

    def _load_data(self):
        pass