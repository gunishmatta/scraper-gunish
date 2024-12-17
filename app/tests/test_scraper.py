import pytest
from unittest.mock import MagicMock
from app.models import Product
from app.scraper import Scraper, ScraperConfig
from app.core.interfaces import AbstractDatabase, AbstractCache, AbstractNotifier


@pytest.fixture
def mock_config():
	return ScraperConfig(
		base_url="https://example.com",
		product_card_selector="div.product-card",
		product_title_selector="h2",
		product_price_selector="span.price",
		product_image_selector="img[src]",
		original_price_selector='price',
		retries=2,
		timeout=5,
	)


@pytest.fixture
def mock_db():
	return MagicMock(spec=AbstractDatabase)


@pytest.fixture
def mock_cache():
	return MagicMock(spec=AbstractCache)


@pytest.fixture
def mock_notifier():
	return MagicMock(spec=AbstractNotifier)


@pytest.fixture
def scraper(mock_db, mock_cache, mock_notifier, mock_config):
	return Scraper(db=mock_db, cache=mock_cache, notifier=mock_notifier, config=mock_config)


def test_product_validation_and_saving(scraper, mock_db, mock_cache):
	scraper.db.save_product = MagicMock()
	scraper.cache.is_price_unchanged = MagicMock(return_value=False)
	scraper.cache.update_cache = MagicMock()
	valid_product = Product(title="Valid Product", price=100.0, image_url="http://example.com/image.jpg")
	scraper._save_product_if_valid(valid_product)
	scraper.db.save_product.assert_called_once_with(valid_product)
	scraper.cache.update_cache.assert_called_once_with(valid_product.title, valid_product.price)