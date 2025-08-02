from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import TrendingProduct, SearchHistory, User
from app.schemas import TrendingProductsResponse

class RecommendationService:
    def __init__(self):
        pass
    
    async def get_trending_products(self, country: str, limit: int = 10) -> TrendingProductsResponse:
        """Get trending products based on search patterns"""
        try:
            db = next(get_db())
            
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            trending = db.query(TrendingProduct).filter(
                TrendingProduct.country == country,
                TrendingProduct.last_updated >= seven_days_ago
            ).order_by(desc(TrendingProduct.search_count)).limit(limit).all()
            
            products = []
            for trend in trending:
                products.append({
                    "name": trend.product_name,
                    "search_count": trend.search_count,
                    "category": trend.category
                })
            
            return TrendingProductsResponse(
                products=products,
                total_count=len(products),
                country=country,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            print(f"Error getting trending products: {str(e)}")
            return TrendingProductsResponse(
                products=[],
                total_count=0,
                country=country,
                last_updated=datetime.now()
            )
        finally:
            db.close()
    
    async def get_personalized_recommendations(self, user_ip: str, country: str, limit: int = 10):
        """Get personalized recommendations based on user history"""
        try:
            db = next(get_db())
            
            user = db.query(User).filter(User.ip_address == user_ip).first()
            if not user:
                return []
            
            recent_searches = db.query(SearchHistory).filter(
                SearchHistory.user_id == user.id,
                SearchHistory.search_time >= datetime.now() - timedelta(days=30)
            ).order_by(desc(SearchHistory.search_time)).limit(10).all()
            
            recommendations = []
            for search in recent_searches:
                recommendations.append({
                    "query": search.query,
                    "category": search.category,
                    "search_time": search.search_time.isoformat()
                })
            
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting personalized recommendations: {str(e)}")
            return []
        finally:
            db.close() 