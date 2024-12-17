from fastapi import FastAPI, Query, Depends, HTTPException
from app.scraper import Scraper
from app.database import Database
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

AUTH_TOKEN = "secret-token"
security = HTTPBearer()

app = FastAPI()

db = Database()
scraper = Scraper(db=db, cache=None, notifier=None)

def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized access")

@app.post("/scrape/")
def scrape_catalogue(
    pages_limit: int = Query(5, ge=1, le=100, description="Number of pages to scrape"),
    proxy: str = Query(None, description="Proxy string to use for requests"),
    credentials: HTTPAuthorizationCredentials = Depends(authenticate)
):
    result = scraper.scrape(pages_limit, proxy)
    return {"status": "success", "message": f"{result} products scraped and saved successfully."}
