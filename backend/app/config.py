from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "BI System"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Zoho Books API
    zoho_client_id: str
    zoho_client_secret: str
    zoho_refresh_token: str = ""
    zoho_organization_id: str
    zoho_api_base_url: str = "https://books.zoho.in"
    zoho_accounts_url: str = "https://accounts.zoho.in"
    zoho_redirect_uri: str = "http://localhost:8000/api/auth/zoho/callback"

    # QuickBooks Online (Virtunest Account)
    qb_client_id: str = ""
    qb_client_secret: str = ""
    qb_redirect_uri: str = "http://localhost:8000/api/auth/quickbooks/callback"
    qb_realm_id: str = ""
    qb_refresh_token: str = ""

    # Claude API
    anthropic_api_key: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_email: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
