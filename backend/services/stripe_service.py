"""
Stripe Payment Service

Handles Stripe payment processing for orders:
- Create checkout sessions
- Handle payment success/failure
- Manage order creation on successful payment
"""

import stripe
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from core.config import settings
from models.user import User
from models.cart import Cart
from models.order import Order
from models.orderitem import OrderItem
from services.cart_service import CartService
import logging

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class StripePaymentService:
    """Service for handling Stripe payments"""
    
    @staticmethod
    def create_checkout_session(
        db: Session, 
        user: User,
        success_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for user's cart
        
        Args:
            db: Database session
            user: Current user
            success_url: URL to redirect on successful payment
            cancel_url: URL to redirect on cancelled payment
            
        Returns:
            Dictionary with checkout session details
        """
        try:
            # Get user's cart
            cart = CartService.get_user_cart(db, user.id)
            if not cart or not cart.items:
                raise ValueError("Cart is empty")
            
            # Calculate cart total
            cart_total = CartService.calculate_cart_total(cart)
            if cart_total <= 0:
                raise ValueError("Cart total must be greater than 0")
            
            # Prepare line items for Stripe
            line_items = []
            for cart_item in cart.items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': cart_item.product.name,
                            'description': cart_item.product.description or "",
                            'images': [cart_item.product.picture] if cart_item.product.picture else []
                        },
                        'unit_amount': int(cart_item.product.price * 100),  # Stripe uses cents
                    },
                    'quantity': cart_item.quantity,
                })
            
            # Set default URLs if not provided, and ensure session_id is included
            if not success_url:
                success_url = f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            elif "session_id" not in success_url:
                # Add session_id parameter if not already present
                separator = "&" if "?" in success_url else "?"
                success_url = f"{success_url}{separator}session_id={{CHECKOUT_SESSION_ID}}"
                
            if not cancel_url:
                cancel_url = f"{settings.FRONTEND_URL}/payment/cancel?session_id={{CHECKOUT_SESSION_ID}}"
            elif "session_id" not in cancel_url:
                # Add session_id parameter if not already present
                separator = "&" if "?" in cancel_url else "?"
                cancel_url = f"{cancel_url}{separator}session_id={{CHECKOUT_SESSION_ID}}"
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user.email,
                metadata={
                    'user_id': str(user.id),
                    'cart_id': str(cart.id)
                },
                # Enable automatic tax calculation (optional)
                automatic_tax={'enabled': False}
            )
            
            logger.info(f"Created Stripe checkout session {checkout_session.id} for user {user.id}")
            
            return {
                'checkout_session_id': checkout_session.id,
                'checkout_url': checkout_session.url,
                'total_amount': cart_total,
                'currency': 'usd',
                'expires_at': checkout_session.expires_at
            }
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise ValueError(f"Payment processing error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise ValueError(f"Failed to create payment session: {str(e)}")
    
    @staticmethod
    def handle_successful_payment(db: Session, session_id: str) -> Optional[Order]:
        """
        Handle successful payment and create order
        
        Args:
            db: Database session
            session_id: Stripe checkout session ID
            
        Returns:
            Created order or None if failed
        """
        try:
            # Retrieve the checkout session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            if checkout_session.payment_status != 'paid':
                raise ValueError("Payment was not successful")
            
            # Get user and cart info from metadata
            user_id = int(checkout_session.metadata.get('user_id'))
            cart_id = int(checkout_session.metadata.get('cart_id'))
            
            # Check if order already exists for this session (prevent duplicates)
            existing_order = db.query(Order).filter(Order.stripe_session_id == session_id).first()
            if existing_order:
                logger.info(f"Order already exists for session {session_id}, returning existing order {existing_order.id}")
                return existing_order
            
            # Get user's cart
            cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id).first()
            if not cart:
                raise ValueError("Cart not found")
            
            # Create order
            order = Order(
                customer_id=user_id,
                total_amount=checkout_session.amount_total / 100,  # Convert from cents
                stripe_session_id=session_id
            )
            db.add(order)
            db.flush()  # Get order ID
            
            # Create order items from cart items
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    total_amount=cart_item.price * cart_item.quantity
                )
                db.add(order_item)
            
            # Clear the cart
            CartService.clear_user_cart(db, user_id)
            
            db.commit()
            db.refresh(order)
            
            logger.info(f"Created order {order.id} for successful payment {session_id}")
            return order
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error handling successful payment: {str(e)}")
            db.rollback()
            return None
        except Exception as e:
            logger.error(f"Error handling successful payment: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def handle_failed_payment(db: Session, session_id: str) -> bool:
        """
        Handle failed payment (cart remains unchanged)
        
        Args:
            db: Database session
            session_id: Stripe checkout session ID
            
        Returns:
            True if handled successfully
        """
        try:
            # Retrieve the checkout session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            logger.info(f"Payment failed for session {session_id}, cart remains unchanged")
            
            # Cart stays the same - no action needed
            # You could add analytics/logging here
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {str(e)}")
            return False
    
    @staticmethod
    def get_payment_status(session_id: str) -> Dict[str, Any]:
        """
        Get payment status from Stripe
        
        Args:
            session_id: Stripe checkout session ID
            
        Returns:
            Payment status information
        """
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                'session_id': session_id,
                'payment_status': checkout_session.payment_status,
                'amount_total': checkout_session.amount_total / 100 if checkout_session.amount_total else 0,
                'currency': checkout_session.currency,
                'customer_email': checkout_session.customer_email,
                'created': checkout_session.created,
                'expires_at': checkout_session.expires_at
            }
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error getting payment status: {str(e)}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def refund_payment(session_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Refund a payment (for admin use)
        
        Args:
            session_id: Stripe checkout session ID
            amount: Amount to refund (None for full refund)
            
        Returns:
            Refund information
        """
        try:
            # Get the checkout session
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            if checkout_session.payment_status != 'paid':
                raise ValueError("Payment was not successful, cannot refund")
            
            # Get payment intent
            payment_intent = checkout_session.payment_intent
            
            # Create refund
            refund_params = {'payment_intent': payment_intent}
            if amount:
                refund_params['amount'] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info(f"Created refund {refund.id} for session {session_id}")
            
            return {
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'currency': refund.currency,
                'status': refund.status,
                'reason': refund.reason
            }
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error creating refund: {str(e)}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Error creating refund: {str(e)}")
            return {'error': str(e)}