from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_token: str
    base_url: str = "https://dentalstall.com/shop/"
    product_card_selector: str = "li.product"
    product_title_selector: str = "h2"
    product_price_selector: str = "span.price ins span.woocommerce-Price-amount"
    original_price_selector: str = "del span.woocommerce-Price-amount"
    product_image_selector: str = "a img.attachment-woocommerce_thumbnail"

    class Config:
        env_file = ".env"


settings = Settings()
