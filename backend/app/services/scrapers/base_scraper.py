from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import httpx
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import uuid

from app.schemas import ProductResponse
from app.config import settings

class BaseScraper(ABC):
    def __init__(self):
        self.timeout = settings.SCRAPER_TIMEOUT
        self.user_agent = settings.SCRAPER_USER_AGENT
        self.delay = settings.SCRAPER_DELAY
    
    @abstractmethod
    async def search_products(
        self, 
        query: str, 
        site_config: Dict[str, Any],
        country: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[ProductResponse]:
        """Search for products on the specific e-commerce site"""
        pass
    
    @abstractmethod
    async def get_product_details(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information from a specific URL"""
        pass
    
    async def _get_page_with_playwright(self, url: str) -> Optional[Page]:
        """Get a page using Playwright for JavaScript-heavy sites"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set user agent
                await page.set_extra_http_headers({
                    "User-Agent": self.user_agent
                })
                
                # Navigate to URL
                await page.goto(url, wait_until="networkidle", timeout=self.timeout)
                
                # Wait for content to load
                await page.wait_for_timeout(2000)
                
                return page
                
        except Exception as e:
            print(f"Error with Playwright: {str(e)}")
            return None
    
    async def _get_page_with_httpx(self, url: str) -> Optional[str]:
        """Get page content using httpx for simple sites"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent}
                )
                
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    return None
                    
        except Exception as e:
            print(f"Error with httpx: {str(e)}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and non-numeric characters
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    def _extract_rating(self, rating_text: str) -> Optional[float]:
        """Extract numeric rating from text"""
        if not rating_text:
            return None
        
        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
        if rating_match:
            try:
                rating = float(rating_match.group(1))
                return min(5.0, max(0.0, rating))  # Ensure rating is between 0-5
            except ValueError:
                return None
        
        return None
    
    def _extract_review_count(self, review_text: str) -> Optional[int]:
        """Extract review count from text"""
        if not review_text:
            return None
        
        count_match = re.search(r'(\d+)', review_text.replace(',', ''))
        if count_match:
            try:
                return int(count_match.group(1))
            except ValueError:
                return None
        
        return None
    
    def _create_product_response(
        self,
        name: str,
        price: float,
        product_url: str,
        store_name: str,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        original_price: Optional[float] = None,
        currency: str = "USD",
        category: Optional[str] = None,
        brand: Optional[str] = None,
        rating: Optional[float] = None,
        review_count: Optional[int] = None,
        availability: bool = True,
        country: str = "Unknown"
    ) -> ProductResponse:
        """Create a ProductResponse object with the given data"""
        return ProductResponse(
            id=str(uuid.uuid4()),
            name=self._clean_text(name),
            description=self._clean_text(description) if description else None,
            price=price,
            original_price=original_price,
            currency=currency,
            image_url=image_url,
            product_url=product_url,
            store_name=store_name,
            store_url=None,
            category=category,
            brand=brand,
            rating=rating,
            review_count=review_count,
            availability=availability,
            country=country,
            scraped_at=datetime.now()
        ) 