from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductRecommendation(BaseModel):
    product_id: int
    name: str
    price: float
    brand: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    picture: Optional[str] = None
    score: float
    reason: str

class RecommendationRequest(BaseModel):
    product_id: int
    limit: Optional[int] = 10
    min_support: Optional[int] = 2

class UserRecommendationRequest(BaseModel):
    user_id: int
    limit: Optional[int] = 10

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    ratings: Optional[int] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    picture: Optional[str] = None

class OrderHistory(BaseModel):
    order_id: int
    customer_id: int
    products: List[int]
    total_amount: float
    created_at: datetime