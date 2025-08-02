import asyncio
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re
import json
from datetime import datetime
import uuid

from app.schemas import ProductResponse
from app.config import settings
from app.services.scrapers.jumia_scraper import JumiaScraper
from app.services.scrapers.amazon_scraper import AmazonScraper
from app.services.scrapers.base_scraper import BaseScraper

class ScraperService:
    def __init__(self):
        self.scrapers = {
            "jumia": JumiaScraper(),
            "amazon": AmazonScraper(),
            # Add more scrapers here
        }
        self.timeout = settings.SCRAPER_TIMEOUT
        self.user_agent = settings.SCRAPER_USER_AGENT
    
    async def search_products(
        self, 
        query: str, 
        country: str, 
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[ProductResponse]:
        """Search for products across multiple e-commerce sites"""
        try:
            # Get relevant sites for the country
            geoip_service = __import__('app.services.geoip_service', fromlist=['GeoIPService']).GeoIPService()
            relevant_sites = geoip_service.get_relevant_sites_for_country(country)
            
            # Prepare search tasks
            search_tasks = []
            
            # Add local site scrapers
            for site_name, site_config in relevant_sites["local"].items():
                if site_config.get("enabled", True) and site_name in self.scrapers:
                    task = self._scrape_site(
                        site_name, 
                        query, 
                        site_config, 
                        country,
                        category,
                        limit // 2  # Prioritize local results
                    )
                    search_tasks.append(task)
            
            # Add international site scrapers
            for site_name, site_config in relevant_sites["international"].items():
                if site_config.get("enabled", True) and site_name in self.scrapers:
                    task = self._scrape_site(
                        site_name, 
                        query, 
                        site_config, 
                        country,
                        category,
                        limit // 2
                    )
                    search_tasks.append(task)
            
            # Execute all scraping tasks concurrently
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine and process results
            all_products = []
            for result in results:
                if isinstance(result, list):
                    all_products.extend(result)
                elif isinstance(result, Exception):
                    print(f"Scraping error: {str(result)}")
            
            # Sort by price and apply markup
            all_products = self._apply_markup_and_sort(all_products)
            
            # Return top results
            return all_products[:limit]
            
        except Exception as e:
            print(f"Error in search_products: {str(e)}")
            return []
    
    async def _scrape_site(
        self, 
        site_name: str, 
        query: str, 
        site_config: Dict[str, Any],
        country: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[ProductResponse]:
        """Scrape products from a specific site"""
        try:
            scraper = self.scrapers.get(site_name)
            if not scraper:
                print(f"No scraper found for site: {site_name}")
                return []
            
            products = await scraper.search_products(
                query=query,
                site_config=site_config,
                country=country,
                category=category,
                limit=limit
            )
            
            return products
            
        except Exception as e:
            print(f"Error scraping {site_name}: {str(e)}")
            return []
    
    def _apply_markup_and_sort(self, products: List[ProductResponse]) -> List[ProductResponse]:
        """Apply markup to products and sort by final price"""
        for product in products:
            # Calculate markup
            markup_amount = self._calculate_markup(product.price)
            product.price = product.price + markup_amount
        
        # Sort by final price (lowest first)
        products.sort(key=lambda x: x.price)
        return products
    
    def _calculate_markup(self, original_price: float) -> float:
        """Calculate markup amount based on revenue model"""
        # Percentage markup
        percentage_markup = original_price * (settings.MARKUP_PERCENTAGE / 100)
        
        # Ensure markup is within min/max bounds
        markup = max(settings.MIN_MARKUP_AMOUNT, percentage_markup)
        markup = min(settings.MAX_MARKUP_AMOUNT, markup)
        
        return round(markup, 2)
    
    async def compare_product_prices(
        self, 
        product_id: str, 
        country: str
    ) -> Dict[str, Any]:
        """Compare prices for a specific product across multiple sites"""
        try:
            # This would typically involve:
            # 1. Getting product details from database
            # 2. Searching for the same product on other sites
            # 3. Comparing prices
            
            # For now, return a mock comparison
            return {
                "product_id": product_id,
                "product_name": "Sample Product",
                "original_price": 29.99,
                "markup_amount": 1.50,
                "final_price": 31.49,
                "currency": "USD",
                "store_name": "Sample Store",
                "product_url": "https://example.com/product",
                "compared_at": datetime.now()
            }
            
        except Exception as e:
            print(f"Error comparing product prices: {str(e)}")
            return {}
    
    async def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get autocomplete suggestions for search queries"""
        try:
            # Common product categories and terms
            common_suggestions = [
                "smartphone", "laptop", "headphones", "shoes", "dress",
                "book", "watch", "camera", "gaming", "fitness",
                "kitchen", "home", "beauty", "electronics", "clothing"
            ]
            
            # Filter suggestions based on query
            filtered_suggestions = [
                suggestion for suggestion in common_suggestions
                if query.lower() in suggestion.lower()
            ]
            
            # Add query-based suggestions
            if query.lower() not in filtered_suggestions:
                filtered_suggestions.insert(0, query)
            
            return filtered_suggestions[:limit]
            
        except Exception as e:
            print(f"Error getting search suggestions: {str(e)}")
            return [query]
    
    async def get_product_details(self, product_url: str, site_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information from a specific URL"""
        try:
            scraper = self.scrapers.get(site_name)
            if not scraper:
                return None
            
            details = await scraper.get_product_details(product_url)
            return details
            
        except Exception as e:
            print(f"Error getting product details: {str(e)}")
            return None 