from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def convert_asyncpg(cls, v: str) -> str:
        if v and v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql+asyncpg://", "postgresql://", 1)
        return v


    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    REDIS_URL: str
    DB_POOL_SIZE: int = 2
    DB_MAX_OVERFLOW: int = 2
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 900
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    REFRESH_TOKEN_COOKIE_SECURE: bool = False
    REFRESH_TOKEN_COOKIE_SAMESITE: str = "lax"

    # SMTP Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    MAIL_FROM: str
    
    class Config:
        env_file = ".env"

settings = Settings()
