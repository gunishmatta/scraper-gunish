from abc import ABC, abstractmethod

from app.models import Product


class AbstractDatabase(ABC):
    @abstractmethod
    def save_product(self, product: Product):
        pass

class AbstractCache(ABC):
    @abstractmethod
    def is_price_unchanged(self, product_title: str, price: float) -> bool:
        pass

    @abstractmethod
    def update_cache(self, product_title: str, price: float):
        pass

class AbstractNotifier(ABC):
    @abstractmethod
    def notify(self, message: str):
        pass
