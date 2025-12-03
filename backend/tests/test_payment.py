"""
Payment Endpoint Tests

This module tests all payment-related endpoints:
- POST /api/payment/create-checkout-session - Create Stripe checkout
- GET /api/payment/status/{session_id} - Get payment status
- POST /api/payment/success/{session_id} - Handle payment success
- POST /api/payment/cancel/{session_id} - Handle payment cancellation
- POST /api/payment/webhook - Stripe webhook handler
- POST /api/payment/refund/{session_id} - Refund payment (Admin only)

Test Coverage:
- Checkout session creation
- Payment status retrieval
- Success/cancel handling
- Order creation on successful payment
- Cart preservation on cancellation
- Admin refund functionality
- Authentication and authorization
- Error handling and edge cases
- Stripe service mocking

Note: These tests mock Stripe API calls to avoid actual payment processing
"""

from fastapi import status
from unittest.mock import patch, MagicMock


class TestCreateCheckoutSession:
    """Test cases for creating Stripe checkout sessions"""
    
    def test_create_checkout_without_auth(self, client, cart_with_items):
        """Test creating checkout without authentication fails"""
        response = client.post(
            "/api/payment/create-checkout-session",
            json={}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_success(self, mock_stripe, client, auth_headers, cart_with_items):
        """Test successfully creating checkout session"""
        # Mock Stripe response
        mock_stripe.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={
                "success_url": "http://localhost:3000/success",
                "cancel_url": "http://localhost:3000/cancel"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "checkout_session_id" in data
        assert "checkout_url" in data
        assert "total_amount" in data
        assert "currency" in data
        assert data["currency"] == "usd"
    
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_default_urls(self, mock_stripe, client, auth_headers, cart_with_items):
        """Test creating checkout without custom URLs uses defaults"""
        mock_stripe.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify Stripe was called with default URLs
        mock_stripe.assert_called_once()
        call_args = mock_stripe.call_args[1]
        assert 'success_url' in call_args
        assert 'cancel_url' in call_args
    
    def test_create_checkout_empty_cart(self, client, auth_headers):
        """Test creating checkout with empty cart fails"""
        response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.json()["detail"].lower()
    
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_correct_line_items(self, mock_stripe, client, auth_headers, cart_with_items):
        """Test checkout session includes correct line items from cart"""
        mock_stripe.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify line items were passed to Stripe
        call_args = mock_stripe.call_args[1]
        line_items = call_args['line_items']
        
        # Should have 2 items (from cart_with_items fixture)
        assert len(line_items) == 2
        
        # Verify item structure
        for item in line_items:
            assert 'price_data' in item
            assert 'quantity' in item
            assert item['price_data']['currency'] == 'usd'
    
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_correct_total(self, mock_stripe, client, auth_headers, cart_with_items):
        """Test checkout session total matches cart total"""
        mock_stripe.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        
        data = response.json()
        expected_total = (999.99 * 2) + (899.99 * 1)  # iPhone x2 + Samsung x1
        assert abs(data["total_amount"] - expected_total) < 0.01
    
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_includes_metadata(self, mock_stripe, client, auth_headers, cart_with_items, test_user):
        """Test checkout session includes user metadata"""
        mock_stripe.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        
        call_args = mock_stripe.call_args[1]
        metadata = call_args['metadata']
        
        assert 'user_id' in metadata
        assert 'cart_id' in metadata
        assert metadata['user_id'] == str(test_user.id)
    
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_stripe_error(self, mock_stripe, client, auth_headers, cart_with_items):
        """Test handling of Stripe API errors"""
        import stripe as stripe_module
        mock_stripe.side_effect = stripe_module.StripeError("Stripe API error")
        
        response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetPaymentStatus:
    """Test cases for retrieving payment status"""
    
    def test_get_status_without_auth(self, client):
        """Test getting status without authentication fails"""
        response = client.get("/api/payment/status/cs_test_123")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_get_status_success(self, mock_retrieve, client, auth_headers):
        """Test successfully retrieving payment status"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='paid',
            amount_total=100000,  # $1000 in cents
            currency='usd',
            customer_email='test@example.com',
            created=1234567890,
            expires_at=1234567900
        )
        
        response = client.get(
            "/api/payment/status/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "cs_test_123"
        assert data["payment_status"] == "paid"
        assert data["amount_total"] == 1000.0  # Converted from cents
        assert data["currency"] == "usd"
        assert data["customer_email"] == "test@example.com"
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_get_status_unpaid(self, mock_retrieve, client, auth_headers):
        """Test retrieving status for unpaid session"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='unpaid',
            amount_total=50000,
            currency='usd',
            customer_email='test@example.com',
            created=1234567890,
            expires_at=1234567900
        )
        
        response = client.get(
            "/api/payment/status/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["payment_status"] == "unpaid"
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_get_status_stripe_error(self, mock_retrieve, client, auth_headers):
        """Test handling Stripe error when retrieving status"""
        import stripe as stripe_module
        mock_retrieve.side_effect = stripe_module.StripeError("Session not found")
        
        response = client.get(
            "/api/payment/status/cs_test_invalid",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestHandlePaymentSuccess:
    """Test cases for handling successful payments"""
    
    def test_handle_success_without_auth(self, client):
        """Test handling success without authentication fails"""
        response = client.post("/api/payment/success/cs_test_123")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_handle_success_creates_order(self, mock_retrieve, client, auth_headers, cart_with_items, test_user):
        """Test successful payment creates order and clears cart"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='paid',
            amount_total=289997,  # $2899.97 in cents
            metadata={'user_id': str(test_user.id), 'cart_id': '1'}
        )
        
        response = client.post(
            "/api/payment/success/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "order_id" in data
        assert "total_amount" in data
        assert "session_id" in data
        assert data["message"] == "Payment successful, order created"
        
        # Verify cart is cleared
        cart_response = client.get("/api/cart/", headers=auth_headers)
        assert len(cart_response.json()["items"]) == 0
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_handle_success_order_has_stripe_session(self, mock_retrieve, client, auth_headers, cart_with_items, test_user):
        """Test created order includes Stripe session ID"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='paid',
            amount_total=289997,
            metadata={'user_id': str(test_user.id), 'cart_id': '1'}
        )
        
        response = client.post(
            "/api/payment/success/cs_test_123",
            headers=auth_headers
        )
        
        order_id = response.json()["order_id"]
        
        # Verify order has session ID
        order_response = client.get(f"/api/orders/{order_id}", headers=auth_headers)
        order_data = order_response.json()
        assert order_data["stripe_session_id"] == "cs_test_123"
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_handle_success_unpaid_session_fails(self, mock_retrieve, client, auth_headers, cart_with_items, test_user):
        """Test handling success for unpaid session fails"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='unpaid',
            metadata={'user_id': str(test_user.id), 'cart_id': '1'}
        )
        
        response = client.post(
            "/api/payment/success/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_handle_success_idempotent(self, mock_retrieve, client, auth_headers, cart_with_items, test_user):
        """Test handling same successful payment twice returns same order"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='paid',
            amount_total=289997,
            metadata={'user_id': str(test_user.id), 'cart_id': '1'}
        )
        
        # First call creates order
        response1 = client.post(
            "/api/payment/success/cs_test_123",
            headers=auth_headers
        )
        order_id_1 = response1.json()["order_id"]
        
        # Recreate cart for second call
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 1})
        
        # Second call with same session should return existing order
        response2 = client.post(
            "/api/payment/success/cs_test_123",
            headers=auth_headers
        )
        order_id_2 = response2.json()["order_id"]
        
        assert order_id_1 == order_id_2


class TestHandlePaymentCancel:
    """Test cases for handling payment cancellation"""
    
    def test_handle_cancel_without_auth(self, client):
        """Test handling cancel without authentication fails"""
        response = client.post("/api/payment/cancel/cs_test_123")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_handle_cancel_preserves_cart(self, mock_retrieve, client, auth_headers, cart_with_items):
        """Test cancelling payment preserves cart"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='unpaid'
        )
        
        # Get initial cart state
        initial_cart = client.get("/api/cart/", headers=auth_headers)
        initial_items = len(initial_cart.json()["items"])
        
        # Cancel payment
        response = client.post(
            "/api/payment/cancel/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cancelled" in data["message"].lower() or "cancel" in data["message"].lower()
        
        # Verify cart is preserved
        cart_response = client.get("/api/cart/", headers=auth_headers)
        assert len(cart_response.json()["items"]) == initial_items
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_handle_cancel_returns_success(self, mock_retrieve, client, auth_headers):
        """Test cancel handler returns success message"""
        mock_retrieve.return_value = MagicMock(id='cs_test_123')
        
        response = client.post(
            "/api/payment/cancel/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "session_id" in response.json()


class TestStripeWebhook:
    """Test cases for Stripe webhook handling"""
    
    def test_webhook_endpoint_exists(self, client):
        """Test webhook endpoint is accessible"""
        response = client.post(
            "/api/payment/webhook",
            headers={"stripe-signature": "test_sig"}
        )
        
        # Should not be 404
        assert response.status_code != status.HTTP_404_NOT_FOUND
    
    def test_webhook_without_signature(self, client):
        """Test webhook without signature"""
        response = client.post("/api/payment/webhook")
        
        # Webhook should handle missing signature
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ]


class TestRefundPayment:
    """Test cases for payment refunds (admin only)"""
    
    def test_refund_without_auth(self, client):
        """Test refund without authentication fails"""
        response = client.post("/api/payment/refund/cs_test_123")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_refund_as_customer(self, client, auth_headers):
        """Test non-admin cannot refund payments"""
        response = client.post(
            "/api/payment/refund/cs_test_123",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('services.stripe_service.stripe.Refund.create')
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_refund_as_admin_success(self, mock_retrieve, mock_refund, client, admin_headers):
        """Test admin can successfully refund payment"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='paid',
            payment_intent='pi_test_123'
        )
        mock_refund.return_value = MagicMock(
            id='re_test_123',
            amount=100000,
            currency='usd',
            status='succeeded',
            reason=None
        )
        
        response = client.post(
            "/api/payment/refund/cs_test_123",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "refund_id" in data
        assert "amount" in data
        assert "status" in data
        assert data["message"] == "Refund processed successfully"
    
    @patch('services.stripe_service.stripe.Refund.create')
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_refund_partial_amount(self, mock_retrieve, mock_refund, client, admin_headers):
        """Test admin can refund partial amount"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='paid',
            payment_intent='pi_test_123'
        )
        mock_refund.return_value = MagicMock(
            id='re_test_123',
            amount=50000,  # $500
            currency='usd',
            status='succeeded',
            reason=None
        )
        
        response = client.post(
            "/api/payment/refund/cs_test_123?amount=500.00",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify refund was called with correct amount
        mock_refund.assert_called_once()
        call_args = mock_refund.call_args[1]
        assert call_args['amount'] == 50000  # $500 in cents
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    def test_refund_unpaid_session_fails(self, mock_retrieve, client, admin_headers):
        """Test refunding unpaid session fails"""
        mock_retrieve.return_value = MagicMock(
            id='cs_test_123',
            payment_status='unpaid'
        )
        
        response = client.post(
            "/api/payment/refund/cs_test_123",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPaymentIntegration:
    """Integration tests for complete payment flow"""
    
    @patch('services.stripe_service.stripe.Refund.create')
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_complete_payment_flow(self, mock_create, mock_retrieve, mock_refund, 
                                   client, auth_headers, sample_products):
        """Test complete flow: add to cart -> checkout -> pay -> order created"""
        # Setup mocks
        mock_create.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        # Add items to cart
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        # Create checkout session
        checkout_response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        assert checkout_response.status_code == status.HTTP_200_OK
        session_id = checkout_response.json()["checkout_session_id"]
        
        # Simulate successful payment
        mock_retrieve.return_value = MagicMock(
            id=session_id,
            payment_status='paid',
            amount_total=199998,  # $1999.98 in cents
            metadata={'user_id': '1', 'cart_id': '1'}
        )
        
        success_response = client.post(
            f"/api/payment/success/{session_id}",
            headers=auth_headers
        )
        assert success_response.status_code == status.HTTP_200_OK
        
        # Verify order was created
        orders_response = client.get("/api/orders/", headers=auth_headers)
        assert len(orders_response.json()) == 1
        
        # Verify cart is empty
        cart_response = client.get("/api/cart/", headers=auth_headers)
        assert len(cart_response.json()["items"]) == 0
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_cancel_preserves_cart_for_retry(self, mock_create, mock_retrieve,
                                             client, auth_headers, sample_products):
        """Test cancelled payment preserves cart for retry"""
        mock_create.return_value = MagicMock(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        # Add item to cart
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        # Create checkout
        checkout_response = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        session_id = checkout_response.json()["checkout_session_id"]
        
        # Cancel payment
        mock_retrieve.return_value = MagicMock(id=session_id, payment_status='unpaid')
        client.post(f"/api/payment/cancel/{session_id}", headers=auth_headers)
        
        # Verify cart still has items
        cart_response = client.get("/api/cart/", headers=auth_headers)
        assert len(cart_response.json()["items"]) == 1
        
        # User can create new checkout session
        checkout_response2 = client.post(
            "/api/payment/create-checkout-session",
            headers=auth_headers,
            json={}
        )
        assert checkout_response2.status_code == status.HTTP_200_OK
