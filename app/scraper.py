from app.database import Database

class Scraper:
    def __init__(self, db: Database, cache, notifier):
        self.db = db
        self.cache = cache
        self.notifier = notifier

    def scrape(self, pages_limit: int, proxy: str = None):
        pass

    def _save_image(self, url: str, product_title: str):
        pass