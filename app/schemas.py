from typing import Optional

from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    num_pages: Optional[int] = None
    proxy: Optional[str] = None