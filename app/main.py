import logging

from fastapi import FastAPI
from app.api.endpoints import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
app = FastAPI(title="Scraper API", version="1.0.0")

app.include_router(router)