from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_scraper
from app.core.auth import authenticate
from app.scraper import Scraper

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "Service is live.", "status": "success"}


@router.post("/scrape/")
def scrape_catalogue(
    pages_limit: int = Query(5, ge=1, le=100, description="Number of pages to scrape"),
    proxy: str = Query(None, description="Proxy string to use for requests"),
    scraper: Scraper = Depends(get_scraper),
    _: None = Depends(authenticate),
):
    result = scraper.scrape(pages_limit, proxy)
    return {"status": "success", "message": f"{result} products scraped and saved successfully."}
