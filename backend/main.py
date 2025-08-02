from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional
import httpx
import json

from app.database import engine, Base
from app.models import User, Product, SearchHistory, PriceComparison
from app.schemas import (
    ProductSearch, ProductResponse, PriceComparisonResponse,
    UserLocation, SearchHistoryResponse, TrendingProductsResponse
)
from app.services.geoip_service import GeoIPService
from app.services.scraper_service import ScraperService
from app.services.recommendation_service import RecommendationService
from app.services.user_tracking_service import UserTrackingService
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Price Comparison Platform...")
    yield
    # Shutdown
    print("Shutting down Price Comparison Platform...")

app = FastAPI(
    title="Global Price Comparison Platform",
    description="A comprehensive price comparison platform for global e-commerce",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
geoip_service = GeoIPService()
scraper_service = ScraperService()
recommendation_service = RecommendationService()
user_tracking_service = UserTrackingService()

@app.get("/")
async def root():
    return {"message": "Global Price Comparison Platform API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "price-comparison-api"}

@app.get("/api/user/location", response_model=UserLocation)
async def get_user_location(request: Request):
    """Detect user's location based on IP address"""
    try:
        client_ip = request.client.host
        location = await geoip_service.get_location_by_ip(client_ip)
        return location
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect location: {str(e)}")

@app.post("/api/search", response_model=List[ProductResponse])
async def search_products(search: ProductSearch, request: Request):
    """Search for products across multiple e-commerce sites"""
    try:
        # Get user location
        client_ip = request.client.host
        location = await geoip_service.get_location_by_ip(client_ip)
        
        # Track search
        await user_tracking_service.track_search(
            query=search.query,
            user_ip=client_ip,
            country=location.country,
            category=search.category
        )
        
        # Scrape products from relevant sites
        products = await scraper_service.search_products(
            query=search.query,
            country=location.country,
            category=search.category,
            limit=search.limit or 20
        )
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/products/{product_id}/compare", response_model=PriceComparisonResponse)
async def compare_product_prices(product_id: str, request: Request):
    """Get price comparison for a specific product"""
    try:
        client_ip = request.client.host
        location = await geoip_service.get_location_by_ip(client_ip)
        
        comparison = await scraper_service.compare_product_prices(
            product_id=product_id,
            country=location.country
        )
        
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price comparison failed: {str(e)}")

@app.get("/api/search/autocomplete")
async def search_autocomplete(q: str, limit: int = 10):
    """Get autocomplete suggestions for search queries"""
    try:
        suggestions = await scraper_service.get_search_suggestions(q, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete failed: {str(e)}")

@app.get("/api/user/history", response_model=List[SearchHistoryResponse])
async def get_user_search_history(request: Request, limit: int = 20):
    """Get user's search history"""
    try:
        client_ip = request.client.host
        history = await user_tracking_service.get_search_history(client_ip, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search history: {str(e)}")

@app.get("/api/recommendations/trending", response_model=TrendingProductsResponse)
async def get_trending_products(request: Request, limit: int = 10):
    """Get trending products based on search patterns"""
    try:
        client_ip = request.client.host
        location = await geoip_service.get_location_by_ip(client_ip)
        
        trending = await recommendation_service.get_trending_products(
            country=location.country,
            limit=limit
        )
        
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending products: {str(e)}")

@app.get("/api/recommendations/personalized")
async def get_personalized_recommendations(request: Request, limit: int = 10):
    """Get personalized product recommendations"""
    try:
        client_ip = request.client.host
        location = await geoip_service.get_location_by_ip(client_ip)
        
        recommendations = await recommendation_service.get_personalized_recommendations(
            user_ip=client_ip,
            country=location.country,
            limit=limit
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@app.get("/api/analytics/search-stats")
async def get_search_analytics():
    """Get search analytics for admin dashboard"""
    try:
        stats = await user_tracking_service.get_search_analytics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 