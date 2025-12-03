"""
Payment API Endpoints

Handles Stripe payment integration:
- Create checkout sessions
- Handle payment webhooks
- Check payment status
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from db.deps import get_db
from utils.auth_utils import get_current_active_user
from models.user import User
from services.stripe_service import StripePaymentService
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])

class CreateCheckoutRequest(BaseModel):
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class CheckoutResponse(BaseModel):
    checkout_session_id: str
    checkout_url: str
    total_amount: float
    currency: str

class PaymentStatusResponse(BaseModel):
    session_id: str
    payment_status: str
    amount_total: float
    currency: str
    customer_email: str

@router.post("/create-checkout-session", response_model=CheckoutResponse)
def create_checkout_session(
    request: CreateCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a Stripe checkout session for the user's cart
    """
    try:
        # Create checkout session
        session_data = StripePaymentService.create_checkout_session(
            db=db,
            user=current_user,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        
        return CheckoutResponse(
            checkout_session_id=session_data['checkout_session_id'],
            checkout_url=session_data['checkout_url'],
            total_amount=session_data['total_amount'],
            currency=session_data['currency']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment session"
        )

@router.get("/status/{session_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get payment status for a checkout session
    """
    try:
        status_data = StripePaymentService.get_payment_status(session_id)
        
        if 'error' in status_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=status_data['error']
            )
        
        return PaymentStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment status"
        )

@router.post("/success/{session_id}")
def handle_payment_success(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Handle successful payment - create order and clear cart
    """
    try:
        # Handle successful payment
        order = StripePaymentService.handle_successful_payment(db, session_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process successful payment"
            )
        
        return {
            "message": "Payment successful, order created",
            "order_id": order.id,
            "total_amount": order.total_amount,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment success"
        )

@router.post("/cancel/{session_id}")
def handle_payment_cancel(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Handle cancelled payment - cart remains unchanged
    """
    try:
        # Handle failed/cancelled payment
        success = StripePaymentService.handle_failed_payment(db, session_id)
        
        if not success:
            logger.warning(f"Failed to handle payment cancellation for session {session_id}")
        
        return {
            "message": "Payment cancelled, cart preserved",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error handling payment cancellation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment cancellation"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks for payment events
    
    This endpoint handles webhooks from Stripe to ensure payment processing
    is reliable even if the user closes their browser.
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # For webhook handling, you would need to:
        # 1. Verify the webhook signature using your webhook secret
        # 2. Handle different event types (payment_intent.succeeded, etc.)
        # 3. Update order status accordingly
        
        # This is a placeholder - implement full webhook handling as needed
        logger.info("Received Stripe webhook")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook handling failed"
        )

# Admin endpoints for payment management
@router.post("/refund/{session_id}")
def refund_payment(
    session_id: str,
    amount: Optional[float] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Refund a payment (admin only)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        refund_data = StripePaymentService.refund_payment(session_id, amount)
        
        if 'error' in refund_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=refund_data['error']
            )
        
        return {
            "message": "Refund processed successfully",
            "refund_id": refund_data['refund_id'],
            "amount": refund_data['amount'],
            "status": refund_data['status']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund"
        )