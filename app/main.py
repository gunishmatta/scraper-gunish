from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(title="Scraper API", version="1.0.0")

app.include_router(router)