from pydantic import BaseModel


class Product(BaseModel):
    title: str
    price: float
    image_url: str
    local_image_path: str = None
