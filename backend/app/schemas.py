from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Schemas
class ProductSearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    limit: Optional[int] = Field(default=20, ge=1, le=100)

class UserLocation(BaseModel):
    country: str
    city: Optional[str] = None
    region: Optional[str] = None
    ip_address: str
    timezone: Optional[str] = None

# Response Schemas
class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    currency: str = "USD"
    image_url: Optional[str] = None
    product_url: str
    store_name: str
    store_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    availability: bool = True
    country: str
    scraped_at: datetime
    
    class Config:
        from_attributes = True

class PriceComparisonResponse(BaseModel):
    product_id: str
    product_name: str
    original_price: float
    markup_amount: float
    final_price: float
    currency: str = "USD"
    store_name: str
    product_url: str
    compared_at: datetime
    
    class Config:
        from_attributes = True

class SearchHistoryResponse(BaseModel):
    id: str
    query: str
    category: Optional[str] = None
    country: str
    results_count: int
    search_time: datetime
    
    class Config:
        from_attributes = True

class TrendingProductsResponse(BaseModel):
    products: List[Dict[str, Any]]
    total_count: int
    country: str
    last_updated: datetime

class SearchAnalyticsResponse(BaseModel):
    total_searches: int
    unique_users: int
    top_queries: List[Dict[str, Any]]
    searches_by_country: Dict[str, int]
    searches_by_category: Dict[str, int]
    average_results_per_search: float

class AutocompleteResponse(BaseModel):
    suggestions: List[str]

# Admin Schemas
class ScraperStatusResponse(BaseModel):
    site_name: str
    status: str
    last_run: Optional[datetime] = None
    products_scraped: int
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

class AdminDashboardResponse(BaseModel):
    total_users: int
    total_products: int
    total_searches: int
    total_comparisons: int
    scraper_status: List[ScraperStatusResponse]
    recent_activity: List[Dict[str, Any]] 