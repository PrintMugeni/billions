from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_address = Column(String, unique=True, index=True)
    country = Column(String)
    city = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    search_history = relationship("SearchHistory", back_populates="user")
    price_comparisons = relationship("PriceComparison", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    currency = Column(String, default="USD")
    image_url = Column(String)
    product_url = Column(String, nullable=False)
    store_name = Column(String, nullable=False)
    store_url = Column(String)
    category = Column(String)
    brand = Column(String)
    rating = Column(Float)
    review_count = Column(Integer)
    availability = Column(Boolean, default=True)
    country = Column(String)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    price_comparisons = relationship("PriceComparison", back_populates="product")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    query = Column(String, nullable=False)
    category = Column(String)
    country = Column(String)
    results_count = Column(Integer, default=0)
    search_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="search_history")

class PriceComparison(Base):
    __tablename__ = "price_comparisons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    product_id = Column(String, ForeignKey("products.id"))
    original_price = Column(Float, nullable=False)
    markup_amount = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    compared_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="price_comparisons")
    product = relationship("Product", back_populates="price_comparisons")

class TrendingProduct(Base):
    __tablename__ = "trending_products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_name = Column(String, nullable=False)
    category = Column(String)
    country = Column(String)
    search_count = Column(Integer, default=1)
    avg_price = Column(Float)
    price_range = Column(JSON)  # {"min": 10.0, "max": 50.0}
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ScraperLog(Base):
    __tablename__ = "scraper_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_name = Column(String, nullable=False)
    status = Column(String)  # success, failed, timeout
    products_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    execution_time = Column(Float)  # in seconds
    scraped_at = Column(DateTime(timezone=True), server_default=func.now()) 