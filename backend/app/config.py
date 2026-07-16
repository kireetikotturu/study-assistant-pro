from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_price_id: str
    frontend_url: str = "http://localhost:5173"

    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
