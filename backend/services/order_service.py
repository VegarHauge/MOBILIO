from sqlalchemy.orm import Session
from models.order import Order
from models.orderitem import OrderItem
from services.cart_service import CartService
from typing import List, Optional
from datetime import datetime

class OrderService:
    
    @staticmethod
    def place_order_from_cart(db: Session, user_id: int) -> Optional[Order]:
        """
        Place an order based on the user's current cart.
        This will:
        1. Get the user's cart
        2. Create an order with all cart items
        3. Delete the cart and cart items
        4. Return the created order
        """
        # Get user's cart
        cart = CartService.get_user_cart(db, user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty or does not exist")
        
        # Calculate total amount
        total_amount = CartService.calculate_cart_total(cart)
        
        # Create the order
        order = Order(
            customer_id=user_id,
            total_amount=total_amount,
            created_at=datetime.utcnow()
        )
        db.add(order)
        db.flush()  # Flush to get the order ID
        
        # Create order items from cart items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                total_amount=cart_item.price * cart_item.quantity
            )
            db.add(order_item)
        
        # Delete cart items and cart
        for cart_item in cart.items:
            db.delete(cart_item)
        db.delete(cart)
        
        # Commit all changes
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def get_user_orders(db: Session, user_id: int) -> List[Order]:
        """Get all orders for a specific user"""
        return db.query(Order).filter(Order.customer_id == user_id).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """
        Get an order by ID. 
        If user_id is provided, ensures the order belongs to that user.
        """
        query = db.query(Order).filter(Order.id == order_id)
        if user_id is not None:
            query = query.filter(Order.customer_id == user_id)
        return query.first()
    
    @staticmethod
    def get_all_orders(db: Session) -> List[Order]:
        """Get all orders (admin only)"""
        return db.query(Order).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def update_stripe_session_id(db: Session, order_id: int, stripe_session_id: str) -> Optional[Order]:
        """Update the Stripe session ID for an order (for future Stripe integration)"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        order.stripe_session_id = stripe_session_id
        db.commit()
        db.refresh(order)
        return order