import logging
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

from app.interfaces import AbstractCache, AbstractDatabase, AbstractNotifier
from app.models import Product
from app.utils import save_image_locally

logging.basicConfig(level=logging.INFO)


class ScraperConfig:
    def __init__(
        self,
        base_url: str,
        product_card_selector: str,
        product_title_selector: str,
        product_price_selector: str,
        product_image_selector: str,
        headers: Optional[dict] = None,
        retries: int = 3,
        timeout: int = 10,
    ):
        self.base_url = base_url
        self.product_card_selector = product_card_selector
        self.product_title_selector = product_title_selector
        self.product_price_selector = product_price_selector
        self.product_image_selector = product_image_selector
        self.headers = headers or {"User-Agent": "Mozilla/5.0"}
        self.retries = retries
        self.timeout = timeout


class Scraper:
    def __init__(
        self,
        db: AbstractDatabase,
        cache: AbstractCache,
        notifier: AbstractNotifier,
        config: ScraperConfig,
    ):
        self.db = db
        self.cache = cache
        self.notifier = notifier
        self.config = config
        self.session = requests.Session()

    def scrape(self, pages_limit: int, proxy: Optional[str] = None) -> int:
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

        total_scraped = 0

        for page_number in range(1, pages_limit + 1):
            url = self._build_page_url(page_number)
            logging.info(f"Scraping page {page_number}: {url}")

            page_content = self._fetch_page_content(url)
            if not page_content:
                continue

            product_cards = self._parse_product_cards(page_content)
            total_scraped += self._process_products(product_cards)

        self.notifier.notify(f"{total_scraped} products scraped and updated.")
        return total_scraped

    def _build_page_url(self, page_number: int) -> str:
        return f"{self.config.base_url}/page/{page_number}"

    def _fetch_page_content(self, url: str) -> Optional[str]:
        retries = self.config.retries
        while retries > 0:
            try:
                response = self.session.get(url, headers=self.config.headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.content
            except requests.exceptions.RequestException as e:
                logging.warning(f"Failed to fetch {url}: {e}. Retries left: {retries}")
                retries -= 1
                time.sleep(2)

        logging.error(f"Skipping {url} after max retries.")
        return None

    def _parse_product_cards(self, page_content: str) -> ResultSet[Tag]:
        soup = BeautifulSoup(page_content, "html.parser")
        return soup.select(self.config.product_card_selector)

    def _save_product_if_valid(self, product: Product):
        """Validate product and save to the database if valid."""
        if not product.title:
            print(f"Product validation failed: Missing title for product.")
            return

        if product.price <= 0:
            print(f"Product validation failed: Invalid price for product {product.title}.")
            return

        if not product.image_url:
            print(f"Product validation failed: Missing image URL for product {product.title}.")
            return

        if self.cache.is_price_unchanged(product.title, product.price):
            print(f"Skipping product {product.title} as the price hasn't changed.")
            return

        local_image_path = save_image_locally(product.image_url, product.title)
        product.local_image_path = local_image_path
        self.db.save_product(product)
        self.cache.update_cache(product.title, product.price)
        print(f"Product {product.title} saved successfully.")

    def _process_products(self, product_cards: List[Tag]) -> int:
        total_products = 0
        for card in product_cards:
            title = card.find("h2").text.strip()
            price_tag = card.find("span", class_="price")
            current_price = price_tag.find("ins")
            if current_price:
                current_price = current_price.find("span", class_="woocommerce-Price-amount").text.strip().replace("₹",
                                                                                                                   "").replace(
                    ",", "")
            else:
                current_price = price_tag.find("span", class_="woocommerce-Price-amount").text.strip().replace("₹",
                                                                                                               "").replace(
                    ",", "")

            try:
                current_price = float(current_price)
            except ValueError:
                current_price = 0.0

            original_price = price_tag.find("del")
            if original_price:
                original_price = original_price.find("span", class_="woocommerce-Price-amount").text.strip().replace(
                    "₹", "").replace(",", "")
            else:
                original_price = None

            if original_price:
                try:
                    original_price = float(original_price)
                except ValueError:
                    original_price = None

            image_tag = card.select_one("a img.attachment-woocommerce_thumbnail")
            image_url = None
            if image_tag:
                image_url = image_tag.get("data-lazy-src") or image_tag.get("data-src") or image_tag.get("src")
                print("Image URL:", image_url)
            else:
                print("Image not found")
            product = Product(
                title=title,
                price=current_price,
                original_price=original_price,
                image_url=image_url,
            )

            self._save_product_if_valid(product)
            total_products += 1

        return total_products

    def _parse_product_card(self, card: BeautifulSoup) -> Product:
        title = card.select_one(self.config.product_title_selector).get_text(strip=True)
        price = float(card.select_one(self.config.product_price_selector).get_text(strip=True).replace("$", ""))
        image_url = card.select_one(self.config.product_image_selector)["src"]
        return Product(title=title, price=price, image_url=image_url)
