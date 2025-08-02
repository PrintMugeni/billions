from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote

from app.services.scrapers.base_scraper import BaseScraper
from app.schemas import ProductResponse

class JumiaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Jumia"
    
    async def search_products(
        self, 
        query: str, 
        site_config: Dict[str, Any],
        country: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[ProductResponse]:
        """Search for products on Jumia"""
        try:
            # Construct search URL
            search_url = site_config["search_url"].format(query=quote(query))
            
            # Get page content
            page_content = await self._get_page_with_httpx(search_url)
            if not page_content:
                return []
            
            # Parse products
            products = self._parse_jumia_products(page_content, site_config["base_url"], country)
            
            return products[:limit]
            
        except Exception as e:
            print(f"Error searching Jumia: {str(e)}")
            return []
    
    def _parse_jumia_products(self, html_content: str, base_url: str, country: str) -> List[ProductResponse]:
        """Parse product information from Jumia search results"""
        products = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Jumia product selectors (these may need updates based on actual site structure)
            product_containers = soup.find_all('article', class_='prd') or \
                               soup.find_all('div', class_='card') or \
                               soup.find_all('div', {'data-qa': 'product-card'})
            
            for container in product_containers:
                try:
                    # Extract product name
                    name_elem = container.find('h3') or \
                               container.find('div', class_='name') or \
                               container.find('a', class_='link')
                    
                    if not name_elem:
                        continue
                    
                    name = name_elem.get_text(strip=True)
                    if not name:
                        continue
                    
                    # Extract product URL
                    link_elem = container.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    product_url = link_elem['href']
                    if not product_url.startswith('http'):
                        product_url = urljoin(base_url, product_url)
                    
                    # Extract price
                    price_elem = container.find('div', class_='prc') or \
                                container.find('span', class_='price') or \
                                container.find('div', class_='prc-now')
                    
                    price = None
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price = self._extract_price(price_text)
                    
                    if not price:
                        continue
                    
                    # Extract original price (if on sale)
                    original_price = None
                    original_price_elem = container.find('div', class_='prc-old') or \
                                         container.find('span', class_='old-price')
                    if original_price_elem:
                        original_price_text = original_price_elem.get_text(strip=True)
                        original_price = self._extract_price(original_price_text)
                    
                    # Extract image URL
                    image_url = None
                    img_elem = container.find('img')
                    if img_elem:
                        image_url = img_elem.get('src') or img_elem.get('data-src')
                        if image_url and not image_url.startswith('http'):
                            image_url = urljoin(base_url, image_url)
                    
                    # Extract rating
                    rating = None
                    rating_elem = container.find('div', class_='stars') or \
                                 container.find('span', class_='rating')
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        rating = self._extract_rating(rating_text)
                    
                    # Extract review count
                    review_count = None
                    review_elem = container.find('div', class_='rev') or \
                                 container.find('span', class_='reviews')
                    if review_elem:
                        review_text = review_elem.get_text(strip=True)
                        review_count = self._extract_review_count(review_text)
                    
                    # Create product response
                    product = self._create_product_response(
                        name=name,
                        price=price,
                        product_url=product_url,
                        store_name=self.site_name,
                        image_url=image_url,
                        original_price=original_price,
                        currency="UGX",  # Jumia Uganda uses UGX
                        rating=rating,
                        review_count=review_count,
                        country=country
                    )
                    
                    products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing Jumia product: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error parsing Jumia products: {str(e)}")
        
        return products
    
    async def get_product_details(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information from Jumia product page"""
        try:
            page_content = await self._get_page_with_httpx(product_url)
            if not page_content:
                return None
            
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract detailed information
            details = {}
            
            # Product name
            name_elem = soup.find('h1') or soup.find('div', class_='product-name')
            if name_elem:
                details['name'] = name_elem.get_text(strip=True)
            
            # Price
            price_elem = soup.find('div', class_='prc') or soup.find('span', class_='price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                details['price'] = self._extract_price(price_text)
            
            # Description
            desc_elem = soup.find('div', class_='description') or soup.find('div', class_='product-description')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Brand
            brand_elem = soup.find('div', class_='brand') or soup.find('span', class_='brand-name')
            if brand_elem:
                details['brand'] = brand_elem.get_text(strip=True)
            
            # Category
            category_elem = soup.find('nav', class_='breadcrumb') or soup.find('div', class_='category')
            if category_elem:
                details['category'] = category_elem.get_text(strip=True)
            
            # Images
            images = []
            img_elems = soup.find_all('img', class_='product-image')
            for img in img_elems:
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(src)
            details['images'] = images
            
            # Specifications
            specs = {}
            spec_elems = soup.find_all('div', class_='specification')
            for spec in spec_elems:
                key_elem = spec.find('span', class_='key')
                value_elem = spec.find('span', class_='value')
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    specs[key] = value
            details['specifications'] = specs
            
            return details
            
        except Exception as e:
            print(f"Error getting Jumia product details: {str(e)}")
            return None 