from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/price_comparison"
    
    # API Keys
    GEOIP_API_KEY: Optional[str] = None
    
    # Scraping
    SCRAPER_TIMEOUT: int = 30000  # 30 seconds
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_DELAY: float = 1.0  # Delay between requests
    
    # Revenue Model
    MARKUP_PERCENTAGE: float = 2.0  # 2% markup
    MIN_MARKUP_AMOUNT: float = 1.0  # Minimum $1 markup
    MAX_MARKUP_AMOUNT: float = 5.0  # Maximum $5 markup
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Admin
    ADMIN_SECRET: str = "your-admin-secret-key"
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # E-commerce Sites Configuration
    ECOMMERCE_SITES = {
        "uganda": {
            "jumia": {
                "base_url": "https://www.jumia.co.ug",
                "search_url": "https://www.jumia.co.ug/catalog/?q={query}",
                "enabled": True
            },
            "jiji": {
                "base_url": "https://jiji.ug",
                "search_url": "https://jiji.ug/search?query={query}",
                "enabled": True
            },
            "ubuy": {
                "base_url": "https://www.ubuy.co.ug",
                "search_url": "https://www.ubuy.co.ug/search?q={query}",
                "enabled": True
            },
            "xente": {
                "base_url": "https://xente.co.ug",
                "search_url": "https://xente.co.ug/search?q={query}",
                "enabled": True
            },
            "dondolo": {
                "base_url": "https://dondolo.co.ug",
                "search_url": "https://dondolo.co.ug/search?q={query}",
                "enabled": True
            }
        },
        "international": {
            "amazon": {
                "base_url": "https://www.amazon.com",
                "search_url": "https://www.amazon.com/s?k={query}",
                "enabled": True
            },
            "walmart": {
                "base_url": "https://www.walmart.com",
                "search_url": "https://www.walmart.com/search?q={query}",
                "enabled": True
            },
            "aliexpress": {
                "base_url": "https://www.aliexpress.com",
                "search_url": "https://www.aliexpress.com/wholesale?SearchText={query}",
                "enabled": True
            }
        }
    }
    
    class Config:
        env_file = ".env"

settings = Settings() 