from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.deps import get_db
from services.cart_service import CartService
from models.schemas import AddToCart, UpdateCartItem, CartResponse, CartItemResponse
from models.user import User
from utils.auth_utils import get_current_active_user

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=CartResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the current user's cart"""
    cart = CartService.get_user_cart(db, current_user.id)
    if not cart:
        # Create empty cart if user doesn't have one
        cart = CartService.get_or_create_user_cart(db, current_user.id)
    
    # Calculate total price
    total_price = CartService.calculate_cart_total(cart)
    
    # Convert to response model
    cart_response = CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[CartItemResponse.model_validate(item) for item in cart.items],
        total_price=total_price
    )
    return cart_response

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    add_to_cart: AddToCart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an item to the user's cart"""
    try:
        cart_item = CartService.add_item_to_cart(db, current_user.id, add_to_cart)
        return CartItemResponse.model_validate(cart_item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/items/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    update_data: UpdateCartItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the quantity of a cart item"""
    cart_item = CartService.update_cart_item_quantity(db, current_user.id, cart_item_id, update_data)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id {cart_item_id} not found"
        )
    return CartItemResponse.model_validate(cart_item)

@router.delete("/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove an item from the user's cart"""
    success = CartService.remove_item_from_cart(db, current_user.id, cart_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id {cart_item_id} not found"
        )
    return None

@router.patch("/items/{cart_item_id}/increment", response_model=CartItemResponse)
def increment_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Increment the quantity of a cart item by 1"""
    cart_item = CartService.increment_cart_item(db, current_user.id, cart_item_id)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id {cart_item_id} not found"
        )
    return CartItemResponse.model_validate(cart_item)

@router.patch("/items/{cart_item_id}/decrement", response_model=CartItemResponse)
def decrement_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Decrement the quantity of a cart item by 1"""
    cart_item = CartService.decrement_cart_item(db, current_user.id, cart_item_id)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id {cart_item_id} not found or removed (quantity became 0)"
        )
    return CartItemResponse.model_validate(cart_item)