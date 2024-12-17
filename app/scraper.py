import logging
import time
from typing import List, Optional
import requests
from bs4 import BeautifulSoup, Tag

from app.core.interfaces import AbstractCache, AbstractDatabase, AbstractNotifier
from app.models import Product
from app.utils import save_image_locally

DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
RETRY_DELAY = 2  # Seconds


class ScraperConfig:
    """Configuration for the scraper with CSS selectors, retries, and timeouts."""
    def __init__(
        self,
        base_url: str,
        product_card_selector: str,
        product_title_selector: str,
        product_price_selector: str,
        product_image_selector: str,
        original_price_selector: str,
        headers: Optional[dict] = None,
        retries: int = 3,
        timeout: int = 10,
    ):
        self.base_url = base_url
        self.product_card_selector = product_card_selector
        self.product_title_selector = product_title_selector
        self.product_price_selector = product_price_selector
        self.original_price_selector = original_price_selector
        self.product_image_selector = product_image_selector
        self.headers = headers or DEFAULT_HEADERS
        self.retries = retries
        self.timeout = timeout


class Scraper:
    """Web scraper to extract product data and save it into a database."""
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
        """Scrape product data across multiple pages."""
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
        """Generate paginated URLs dynamically."""
        return f"{self.config.base_url}/page/{page_number}"

    def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch and return page content with retries."""
        retries = self.config.retries
        while retries > 0:
            try:
                response = self.session.get(
                    url, headers=self.config.headers, timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.content
            except requests.exceptions.RequestException as e:
                logging.warning(f"Failed to fetch {url}: {e}. Retries left: {retries}")
                retries -= 1
                time.sleep(RETRY_DELAY)

        logging.error(f"Skipping {url} after max retries.")
        return None

    def _parse_product_cards(self, page_content: str) -> List[Tag]:
        """Parse product cards from page content."""
        soup = BeautifulSoup(page_content, "html.parser")
        return soup.select(self.config.product_card_selector)

    def _process_products(self, product_cards: List[Tag]) -> int:
        """Processes a list of product cards and saves valid products."""
        total_products = 0
        for card in product_cards:
            product = self._extract_product_data(card)
            if product and self._save_product_if_valid(product):
                total_products += 1
        return total_products

    def _extract_product_data(self, card: Tag) -> Optional[Product]:
        """Extract product details from a single product card."""
        try:
            title = self._extract_title(card)
            price = self._extract_price(card)
            original_price = self._extract_original_price(card)
            image_url = self._extract_image_url(card)
            return Product(
                title=title,
                price=price,
                original_price=original_price,
                image_url=image_url,
            )
        except Exception as e:
            logging.error(f"Error extracting product data: {e}")
            return None

    def _extract_title(self, card: Tag) -> str:
        """Extract product title from a product card."""
        return card.select_one(self.config.product_title_selector).get_text(strip=True)

    def _extract_price(self, card: Tag) -> float:
        """Extract product price from a product card."""
        price_tag = self._get_price_tag(card)
        if price_tag:
            return self._convert_price(price_tag)
        return 0.0

    def _get_price_tag(self, card: Tag) -> Optional[Tag]:
        """Get the price tag from the product card."""
        return card.select_one(self.config.product_price_selector) or \
               card.select_one("span.price span.woocommerce-Price-amount")

    def _convert_price(self, price_tag: Tag) -> float:
        """Convert price to float and handle errors."""
        try:
            price_text = price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
            return float(price_text) if price_text else 0.0
        except ValueError:
            logging.error("Failed to convert price to float.")
            return 0.0

    def _extract_original_price(self, card: Tag) -> Optional[float]:
        """Extract original price from a product card."""
        original_price_tag = card.select_one(self.config.original_price_selector)
        if original_price_tag:
            return self._convert_price(original_price_tag)
        return None

    def _extract_image_url(self, card: Tag) -> Optional[str]:
        """Extract image URL from a product card."""
        image_tag = card.select_one(self.config.product_image_selector)
        return (
            image_tag.get("data-lazy-src")
            or image_tag.get("data-src")
            or image_tag.get("src")
            or None
        )

    def _save_product_if_valid(self, product: Product) -> bool:
        """Validate product and save it to the database."""
        if not self._is_valid_product(product):
            logging.warning(f"Invalid product data: {product}")
            return False

        if self.cache.is_price_unchanged(product.title, product.price):
            logging.info(f"Skipping product '{product.title}': Price unchanged.")
            return False

        product.local_image_path = save_image_locally(product.image_url, product.title)
        self.db.save_product(product)
        self.cache.update_cache(product.title, product.price)
        logging.info(f"Product '{product.title}' saved successfully.")
        return True

    def _is_valid_product(self, product: Product) -> bool:
        """Check if the product has valid data."""
        return bool(product.title and product.price > 0 and product.image_url)
