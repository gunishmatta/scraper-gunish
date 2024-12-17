from app.core.cache import RedisCache
from app.core.config import Settings
from app.core.database import JsonDatabase
from app.core.notifications import ConsoleNotifier
from app.scraper import ScraperConfig, Scraper

settings = Settings()

def get_scraper():
    db = JsonDatabase("data/products.json")
    cache = RedisCache()
    notifier = ConsoleNotifier()

    config = ScraperConfig(
        base_url=settings.base_url,
        product_card_selector=settings.product_card_selector,
        product_title_selector=settings.product_title_selector,
        product_price_selector=settings.product_price_selector,
        product_image_selector=settings.product_image_selector,
        original_price_selector=settings.original_price_selector
    )
    return Scraper(db=db, cache=cache, notifier=notifier, config=config)
