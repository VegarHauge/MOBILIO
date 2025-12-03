from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str       

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    sort_option: str
    
    class Config:
        from_attributes = True

class LoginUserResponse(UserBase):
    role: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserResponse  # Include user info for frontend state management

class TokenData(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    brand: Optional[str] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    picture: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    picture: Optional[str] = None

class ProductResponse(BaseModel):
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

    class Config:
        from_attributes = True

# Cart schemas
class AddToCart(BaseModel):
    product_id: int
    quantity: int = 1

class UpdateCartItem(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductResponse

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List['CartItemResponse'] = []
    total_price: Optional[float] = None

    class Config:
        from_attributes = True

# Order schemas
class PlaceOrderRequest(BaseModel):
    """Request to place an order from cart - no additional data needed as we use the user's cart"""
    pass

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_amount: float
    product: ProductResponse

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    created_at: datetime
    stripe_session_id: Optional[str] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True