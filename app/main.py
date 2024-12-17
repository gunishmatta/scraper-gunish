from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis import Redis

from app.cache import RedisCache
from app.database import JsonDatabase
from app.notifications import ConsoleNotifier
from app.scraper import Scraper, ScraperConfig

AUTH_TOKEN = "secret-token"
security = HTTPBearer()

app = FastAPI()

config = ScraperConfig(
    base_url="https://dentalstall.com/shop/",
    product_card_selector="li.product",
    product_title_selector="h2.woo-loop-product__title",
    product_price_selector="span.price ins span.woocommerce-Price-amount",
    product_image_selector="img",
)

db = JsonDatabase("data/products.json")
cache = RedisCache()
notifier = ConsoleNotifier()

scraper = Scraper(db=db, cache=cache, notifier=notifier, config=config)

def authenticate(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized access")

@app.get("/health")
def health():
    return {"data": "Service is live.","status":"success"}

@app.post("/scrape/", dependencies=[Depends(authenticate)])
def scrape_catalogue(
    pages_limit: int = Query(5, ge=1, le=100, description="Number of pages to scrape"),
    proxy: str = Query(None, description="Proxy string to use for requests"),
):
    result = scraper.scrape(pages_limit, proxy)
    return {"status": "success", "message": f"{result} products scraped and saved successfully."}
