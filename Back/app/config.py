from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/cap_table_db"
    
    # JWT
    secret_key: str = "your-secret-key-here-make-it-long-and-secure"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    environment: str = "development"
    
    # Company Info for PDFs
    company_name: str = "Your Company Name"
    company_address: str = "123 Business Street, City, Country"
    company_email: str = "info@yourcompany.com"
    company_website: str = "https://yourcompany.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 