from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.deps import get_db
from services.order_service import OrderService
from models.schemas import OrderResponse
from models.user import User
from utils.auth_utils import get_current_active_user, get_admin_user
from typing import List

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Place an order based on the current user's cart.
    This will create an order with all cart items and clear the cart.
    """
    try:
        order = OrderService.place_order_from_cart(db, current_user.id)
        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[OrderResponse])
def get_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all orders for the current user"""
    orders = OrderService.get_user_orders(db, current_user.id)
    return [OrderResponse.model_validate(order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific order by ID (user can only access their own orders)"""
    order = OrderService.get_order_by_id(db, order_id, current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return OrderResponse.model_validate(order)

@router.get("/admin/all", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all orders (Admin only)"""
    orders = OrderService.get_all_orders(db)
    return [OrderResponse.model_validate(order) for order in orders]

@router.get("/admin/{order_id}", response_model=OrderResponse)
def get_any_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get any order by ID (Admin only - can access any user's order)"""
    order = OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return OrderResponse.model_validate(order)

