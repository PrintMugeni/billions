from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote

from app.services.scrapers.base_scraper import BaseScraper
from app.schemas import ProductResponse

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Amazon"
    
    async def search_products(
        self, 
        query: str, 
        site_config: Dict[str, Any],
        country: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[ProductResponse]:
        """Search for products on Amazon"""
        try:
            # Construct search URL
            search_url = site_config["search_url"].format(query=quote(query))
            
            # Get page content using Playwright (Amazon is JavaScript-heavy)
            page = await self._get_page_with_playwright(search_url)
            if not page:
                return []
            
            # Get page content
            html_content = await page.content()
            await page.close()
            
            # Parse products
            products = self._parse_amazon_products(html_content, site_config["base_url"], country)
            
            return products[:limit]
            
        except Exception as e:
            print(f"Error searching Amazon: {str(e)}")
            return []
    
    def _parse_amazon_products(self, html_content: str, base_url: str, country: str) -> List[ProductResponse]:
        """Parse product information from Amazon search results"""
        products = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Amazon product selectors (these may need updates based on actual site structure)
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'}) or \
                               soup.find_all('div', class_='s-result-item') or \
                               soup.find_all('div', class_='sg-col-inner')
            
            for container in product_containers:
                try:
                    # Extract product name
                    name_elem = container.find('h2') or \
                               container.find('span', class_='a-size-medium') or \
                               container.find('a', class_='a-link-normal')
                    
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
                    
                    # Skip sponsored or non-product links
                    if '/gp/' in product_url or '/ref=' in product_url:
                        continue
                    
                    # Extract price
                    price_elem = container.find('span', class_='a-price-whole') or \
                                container.find('span', class_='a-price') or \
                                container.find('span', class_='a-offscreen')
                    
                    price = None
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price = self._extract_price(price_text)
                    
                    if not price:
                        continue
                    
                    # Extract original price (if on sale)
                    original_price = None
                    original_price_elem = container.find('span', class_='a-text-strike') or \
                                         container.find('span', class_='a-price a-text-price')
                    if original_price_elem:
                        original_price_text = original_price_elem.get_text(strip=True)
                        original_price = self._extract_price(original_price_text)
                    
                    # Extract image URL
                    image_url = None
                    img_elem = container.find('img', class_='s-image') or \
                              container.find('img', {'data-image-latency': True})
                    if img_elem:
                        image_url = img_elem.get('src') or img_elem.get('data-src')
                        if image_url and not image_url.startswith('http'):
                            image_url = urljoin(base_url, image_url)
                    
                    # Extract rating
                    rating = None
                    rating_elem = container.find('span', class_='a-icon-alt') or \
                                 container.find('i', class_='a-icon-star')
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        rating = self._extract_rating(rating_text)
                    
                    # Extract review count
                    review_count = None
                    review_elem = container.find('span', class_='a-size-base') or \
                                 container.find('a', class_='a-link-normal')
                    if review_elem:
                        review_text = review_elem.get_text(strip=True)
                        review_count = self._extract_review_count(review_text)
                    
                    # Extract brand
                    brand = None
                    brand_elem = container.find('span', class_='a-size-base-plus') or \
                                container.find('div', class_='a-row a-size-base a-color-secondary')
                    if brand_elem:
                        brand = brand_elem.get_text(strip=True)
                    
                    # Create product response
                    product = self._create_product_response(
                        name=name,
                        price=price,
                        product_url=product_url,
                        store_name=self.site_name,
                        image_url=image_url,
                        original_price=original_price,
                        currency="USD",  # Amazon typically uses USD
                        brand=brand,
                        rating=rating,
                        review_count=review_count,
                        country=country
                    )
                    
                    products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing Amazon product: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error parsing Amazon products: {str(e)}")
        
        return products
    
    async def get_product_details(self, product_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information from Amazon product page"""
        try:
            page = await self._get_page_with_playwright(product_url)
            if not page:
                return None
            
            html_content = await page.content()
            await page.close()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract detailed information
            details = {}
            
            # Product name
            name_elem = soup.find('span', id='productTitle') or soup.find('h1', class_='a-size-large')
            if name_elem:
                details['name'] = name_elem.get_text(strip=True)
            
            # Price
            price_elem = soup.find('span', class_='a-price-whole') or \
                        soup.find('span', class_='a-offscreen') or \
                        soup.find('span', class_='a-price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                details['price'] = self._extract_price(price_text)
            
            # Description
            desc_elem = soup.find('div', id='productDescription') or \
                       soup.find('div', class_='a-expander-content') or \
                       soup.find('div', id='feature-bullets')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Brand
            brand_elem = soup.find('a', id='bylineInfo') or \
                        soup.find('span', class_='a-size-base a-color-secondary')
            if brand_elem:
                details['brand'] = brand_elem.get_text(strip=True)
            
            # Category
            category_elem = soup.find('nav', class_='a-breadcrumb') or \
                           soup.find('div', id='wayfinding-breadcrumbs')
            if category_elem:
                details['category'] = category_elem.get_text(strip=True)
            
            # Images
            images = []
            img_elems = soup.find_all('img', id='landingImage') or \
                       soup.find_all('img', class_='a-dynamic-image')
            for img in img_elems:
                src = img.get('src') or img.get('data-old-hires')
                if src:
                    images.append(src)
            details['images'] = images
            
            # Specifications
            specs = {}
            spec_elems = soup.find_all('tr', class_='a-spacing-small') or \
                        soup.find_all('div', class_='a-expander-content')
            for spec in spec_elems:
                key_elem = spec.find('td', class_='a-span3')
                value_elem = spec.find('td', class_='a-span9')
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    specs[key] = value
            details['specifications'] = specs
            
            # Availability
            availability_elem = soup.find('div', id='availability') or \
                              soup.find('span', class_='a-size-medium a-color-success')
            if availability_elem:
                availability_text = availability_elem.get_text(strip=True).lower()
                details['availability'] = 'in stock' in availability_text
            
            return details
            
        except Exception as e:
            print(f"Error getting Amazon product details: {str(e)}")
            return None 