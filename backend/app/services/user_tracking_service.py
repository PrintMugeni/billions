from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import json

from app.database import get_db
from app.models import User, SearchHistory, TrendingProduct, ScraperLog
from app.schemas import SearchHistoryResponse, SearchAnalyticsResponse

class UserTrackingService:
    def __init__(self):
        pass
    
    async def track_search(
        self, 
        query: str, 
        user_ip: str, 
        country: str, 
        category: Optional[str] = None
    ) -> None:
        """Track a user search"""
        try:
            db = next(get_db())
            
            # Get or create user
            user = db.query(User).filter(User.ip_address == user_ip).first()
            if not user:
                user = User(
                    ip_address=user_ip,
                    country=country,
                    created_at=datetime.now()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                user.last_seen = datetime.now()
                db.commit()
            
            # Create search history entry
            search_history = SearchHistory(
                user_id=user.id,
                query=query,
                category=category,
                country=country,
                search_time=datetime.now()
            )
            db.add(search_history)
            
            # Update trending products
            await self._update_trending_products(query, category, country, db)
            
            db.commit()
            
        except Exception as e:
            print(f"Error tracking search: {str(e)}")
        finally:
            db.close()
    
    async def get_search_history(self, user_ip: str, limit: int = 20) -> List[SearchHistoryResponse]:
        """Get search history for a user"""
        try:
            db = next(get_db())
            
            user = db.query(User).filter(User.ip_address == user_ip).first()
            if not user:
                return []
            
            history = db.query(SearchHistory).filter(
                SearchHistory.user_id == user.id
            ).order_by(
                desc(SearchHistory.search_time)
            ).limit(limit).all()
            
            return [
                SearchHistoryResponse(
                    id=h.id,
                    query=h.query,
                    category=h.category,
                    country=h.country,
                    results_count=h.results_count,
                    search_time=h.search_time
                ) for h in history
            ]
            
        except Exception as e:
            print(f"Error getting search history: {str(e)}")
            return []
        finally:
            db.close()
    
    async def _update_trending_products(
        self, 
        query: str, 
        category: Optional[str], 
        country: str, 
        db: Session
    ) -> None:
        """Update trending products based on search query"""
        try:
            # Find existing trending product
            trending = db.query(TrendingProduct).filter(
                TrendingProduct.product_name.ilike(f"%{query}%"),
                TrendingProduct.country == country
            ).first()
            
            if trending:
                # Update existing trending product
                trending.search_count += 1
                trending.last_updated = datetime.now()
            else:
                # Create new trending product
                trending = TrendingProduct(
                    product_name=query,
                    category=category,
                    country=country,
                    search_count=1,
                    last_updated=datetime.now()
                )
                db.add(trending)
            
        except Exception as e:
            print(f"Error updating trending products: {str(e)}")
    
    async def get_search_analytics(self) -> SearchAnalyticsResponse:
        """Get search analytics for admin dashboard"""
        try:
            db = next(get_db())
            
            # Total searches
            total_searches = db.query(func.count(SearchHistory.id)).scalar()
            
            # Unique users
            unique_users = db.query(func.count(User.id)).scalar()
            
            # Top queries (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            top_queries = db.query(
                SearchHistory.query,
                func.count(SearchHistory.id).label('count')
            ).filter(
                SearchHistory.search_time >= thirty_days_ago
            ).group_by(
                SearchHistory.query
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Searches by country
            searches_by_country = db.query(
                SearchHistory.country,
                func.count(SearchHistory.id).label('count')
            ).group_by(
                SearchHistory.country
            ).all()
            
            # Searches by category
            searches_by_category = db.query(
                SearchHistory.category,
                func.count(SearchHistory.id).label('count')
            ).filter(
                SearchHistory.category.isnot(None)
            ).group_by(
                SearchHistory.category
            ).all()
            
            # Average results per search
            avg_results = db.query(
                func.avg(SearchHistory.results_count)
            ).scalar() or 0
            
            return SearchAnalyticsResponse(
                total_searches=total_searches,
                unique_users=unique_users,
                top_queries=[
                    {"query": q.query, "count": q.count} 
                    for q in top_queries
                ],
                searches_by_country={
                    s.country: s.count for s in searches_by_country
                },
                searches_by_category={
                    s.category: s.count for s in searches_by_category
                },
                average_results_per_search=float(avg_results)
            )
            
        except Exception as e:
            print(f"Error getting search analytics: {str(e)}")
            return SearchAnalyticsResponse(
                total_searches=0,
                unique_users=0,
                top_queries=[],
                searches_by_country={},
                searches_by_category={},
                average_results_per_search=0.0
            )
        finally:
            db.close()
    
    async def log_scraper_run(
        self, 
        site_name: str, 
        status: str, 
        products_scraped: int = 0,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ) -> None:
        """Log scraper execution results"""
        try:
            db = next(get_db())
            
            log_entry = ScraperLog(
                site_name=site_name,
                status=status,
                products_scraped=products_scraped,
                error_message=error_message,
                execution_time=execution_time,
                scraped_at=datetime.now()
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            print(f"Error logging scraper run: {str(e)}")
        finally:
            db.close()
    
    async def get_user_preferences(self, user_ip: str) -> Dict[str, Any]:
        """Get user preferences based on search history"""
        try:
            db = next(get_db())
            
            user = db.query(User).filter(User.ip_address == user_ip).first()
            if not user:
                return {}
            
            # Get user's most searched categories
            categories = db.query(
                SearchHistory.category,
                func.count(SearchHistory.id).label('count')
            ).filter(
                SearchHistory.user_id == user.id,
                SearchHistory.category.isnot(None)
            ).group_by(
                SearchHistory.category
            ).order_by(
                desc('count')
            ).limit(5).all()
            
            # Get user's most searched queries
            queries = db.query(
                SearchHistory.query,
                func.count(SearchHistory.id).label('count')
            ).filter(
                SearchHistory.user_id == user.id
            ).group_by(
                SearchHistory.query
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            return {
                "preferred_categories": [c.category for c in categories],
                "frequent_queries": [q.query for q in queries],
                "country": user.country,
                "last_seen": user.last_seen.isoformat() if user.last_seen else None
            }
            
        except Exception as e:
            print(f"Error getting user preferences: {str(e)}")
            return {}
        finally:
            db.close() 