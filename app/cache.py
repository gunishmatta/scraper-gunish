import redis

from app.interfaces import AbstractCache


class RedisCache(AbstractCache):
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.client = redis.Redis(host=host, port=port, db=0)

    def is_price_unchanged(self, product_title: str, price: float) -> bool:
        cached_price = self.client.get(product_title)
        return cached_price and float(cached_price) == price

    def update_cache(self, product_title: str, price: float):
        self.client.set(product_title, price)
