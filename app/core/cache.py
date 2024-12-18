import os
import redis
from app.core.interfaces import AbstractCache


class RedisCache(AbstractCache):
    def __init__(self, host: str = os.getenv("REDIS_HOST", "localhost"), port: int = int(os.getenv("REDIS_PORT", 6379))):
        self.client = redis.Redis(host=host, port=port, db=0)

    def is_price_unchanged(self, product_title: str, price: float) -> bool:
        cached_price = self.client.get(product_title)
        return cached_price and float(cached_price) == price

    def update_cache(self, product_title: str, price: float):
        self.client.set(product_title, price)
