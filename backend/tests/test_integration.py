"""
Integration Tests

These tests verify that multiple components work together correctly:
- Complete user workflows across multiple endpoints
- Database transaction integrity
- Service layer interactions
- Multi-user scenarios
- Authentication flow integration
- Payment and order creation flow

Unlike unit tests which mock dependencies, integration tests use:
- Real database operations (SQLite in-memory)
- Real service layer logic
- Real API endpoint interactions
- Only external APIs (Stripe) are mocked
"""

from fastapi import status
from unittest.mock import patch, MagicMock
import pytest


@pytest.mark.integration
class TestCompleteECommerceFlow:
    """Test complete user journey from registration to order completion"""
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_full_user_journey(self, mock_create, mock_retrieve, client, sample_products):
        """
        Integration test: Complete e-commerce flow
        Register → Login → Browse → Add to cart → Checkout → Payment → Order
        """
        # Step 1: Register new user
        register_response = client.post(
            "/api/auth/register",
            json={
                "name": "Integration Test User",
                "email": "integration@test.com",
                "password": "testpass123"
            }
        )
        assert register_response.status_code == status.HTTP_200_OK
        
        # Step 2: Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "integration@test.com",
                "password": "testpass123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Browse products
        products_response = client.get("/api/products/")
        assert products_response.status_code == status.HTTP_200_OK
        assert len(products_response.json()) == 3
        
        # Step 4: Add items to cart
        client.post(
            "/api/cart/items",
            headers=headers,
            json={"product_id": 1, "quantity": 2}
        )
        client.post(
            "/api/cart/items",
            headers=headers,
            json={"product_id": 2, "quantity": 1}
        )
        
        # Step 5: Verify cart
        cart_response = client.get("/api/cart/", headers=headers)
        cart = cart_response.json()
        assert len(cart["items"]) == 2
        initial_total = cart["total_price"]
        
        # Step 6: Create checkout session
        mock_create.return_value = MagicMock(
            id='cs_integration_test',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        
        checkout_response = client.post(
            "/api/payment/create-checkout-session",
            headers=headers,
            json={}
        )
        assert checkout_response.status_code == status.HTTP_200_OK
        session_id = checkout_response.json()["checkout_session_id"]
        
        # Step 7: Simulate successful payment
        mock_retrieve.return_value = MagicMock(
            id=session_id,
            payment_status='paid',
            amount_total=int(initial_total * 100),
            metadata={'user_id': str(register_response.json()["id"]), 'cart_id': '1'}
        )
        
        payment_response = client.post(
            f"/api/payment/success/{session_id}",
            headers=headers
        )
        assert payment_response.status_code == status.HTTP_200_OK
        order_id = payment_response.json()["order_id"]
        
        # Step 8: Verify order was created
        order_response = client.get(f"/api/orders/{order_id}", headers=headers)
        assert order_response.status_code == status.HTTP_200_OK
        order = order_response.json()
        assert len(order["items"]) == 2
        assert abs(order["total_amount"] - initial_total) < 0.01
        
        # Step 9: Verify cart is empty
        final_cart = client.get("/api/cart/", headers=headers)
        assert len(final_cart.json()["items"]) == 0
        
        # Step 10: Verify user can see their order history
        orders_response = client.get("/api/orders/", headers=headers)
        assert len(orders_response.json()) == 1


@pytest.mark.integration
class TestCartToOrderIntegration:
    """Test cart and order service integration"""
    
    def test_cart_quantities_preserved_in_order(self, client, auth_headers, sample_products):
        """Test that cart item quantities are correctly preserved in order"""
        # Add specific quantities to cart
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 5}
        )
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 2, "quantity": 3}
        )
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 3, "quantity": 7}
        )
        
        # Place order
        order_response = client.post("/api/orders/", headers=auth_headers)
        order = order_response.json()
        
        # Verify quantities match
        quantity_map = {item["product_id"]: item["quantity"] for item in order["items"]}
        assert quantity_map[1] == 5
        assert quantity_map[2] == 3
        assert quantity_map[3] == 7
    
    def test_cart_prices_snapshot_in_order(self, client, auth_headers, admin_headers, sample_products, db_session):
        """Test that order items capture price at time of purchase"""
        # Customer adds product to cart
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        # Get original price
        product_response = client.get("/api/products/1")
        original_price = product_response.json()["price"]
        
        # Admin changes product price
        client.put(
            "/api/products/1",
            headers=admin_headers,
            json={"price": 1499.99}  # Increase price
        )
        
        # Customer places order
        order_response = client.post("/api/orders/", headers=auth_headers)
        order = order_response.json()
        
        # Order should have original price, not new price
        order_item = order["items"][0]
        assert abs(order_item["total_amount"] - original_price) < 0.01
    
    def test_multiple_cart_operations_then_order(self, client, auth_headers, sample_products):
        """Test complex cart operations followed by order placement"""
        # Add item
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 2})
        
        # Add another item
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 2, "quantity": 3})
        
        # Increment first item
        cart = client.get("/api/cart/", headers=auth_headers).json()
        item1_id = next(item["id"] for item in cart["items"] if item["product_id"] == 1)
        client.patch(f"/api/cart/items/{item1_id}/increment", headers=auth_headers)
        
        # Decrement second item
        item2_id = next(item["id"] for item in cart["items"] if item["product_id"] == 2)
        client.patch(f"/api/cart/items/{item2_id}/decrement", headers=auth_headers)
        
        # Add third item
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 3, "quantity": 1})
        
        # Remove third item
        cart = client.get("/api/cart/", headers=auth_headers).json()
        item3_id = next(item["id"] for item in cart["items"] if item["product_id"] == 3)
        client.delete(f"/api/cart/items/{item3_id}", headers=auth_headers)
        
        # Place order
        order_response = client.post("/api/orders/", headers=auth_headers)
        order = order_response.json()
        
        # Verify final state: product 1 (qty 3), product 2 (qty 2)
        assert len(order["items"]) == 2
        quantities = {item["product_id"]: item["quantity"] for item in order["items"]}
        assert quantities[1] == 3  # 2 + 1 increment
        assert quantities[2] == 2  # 3 - 1 decrement


@pytest.mark.integration
class TestMultiUserScenarios:
    """Test multiple users interacting with the system simultaneously"""
    
    def test_user_cart_isolation(self, client, auth_headers, admin_headers, sample_products):
        """Test that users have completely isolated carts"""
        # User 1 adds items
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        # User 2 (admin) adds different items
        client.post(
            "/api/cart/items",
            headers=admin_headers,
            json={"product_id": 2, "quantity": 5}
        )
        
        # Verify User 1's cart
        user1_cart = client.get("/api/cart/", headers=auth_headers).json()
        assert len(user1_cart["items"]) == 1
        assert user1_cart["items"][0]["product_id"] == 1
        assert user1_cart["items"][0]["quantity"] == 2
        
        # Verify User 2's cart
        user2_cart = client.get("/api/cart/", headers=admin_headers).json()
        assert len(user2_cart["items"]) == 1
        assert user2_cart["items"][0]["product_id"] == 2
        assert user2_cart["items"][0]["quantity"] == 5
    
    def test_user_order_isolation(self, client, auth_headers, admin_headers, sample_products):
        """Test that users can only see their own orders"""
        # User 1 places order
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 1})
        user1_order = client.post("/api/orders/", headers=auth_headers).json()
        
        # User 2 places order
        client.post("/api/cart/items", headers=admin_headers, json={"product_id": 2, "quantity": 1})
        user2_order = client.post("/api/orders/", headers=admin_headers).json()
        
        # User 1 should only see their order
        user1_orders = client.get("/api/orders/", headers=auth_headers).json()
        assert len(user1_orders) == 1
        assert user1_orders[0]["id"] == user1_order["id"]
        
        # User 2 should only see their order
        user2_orders = client.get("/api/orders/", headers=admin_headers).json()
        assert len(user2_orders) == 1
        assert user2_orders[0]["id"] == user2_order["id"]
        
        # User 1 cannot access User 2's order
        response = client.get(f"/api/orders/{user2_order['id']}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_concurrent_product_updates(self, client, auth_headers, admin_headers, sample_products):
        """Test multiple users ordering same product with stock changes"""
        # Get initial product stock
        product = client.get("/api/products/1").json()
        initial_stock = product["stock"]
        
        # User adds to cart
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 2})
        
        # Admin updates stock (simulating another sale)
        client.put(
            "/api/products/1",
            headers=admin_headers,
            json={"stock": initial_stock - 5}
        )
        
        # User places order (should succeed - no stock validation in current implementation)
        order_response = client.post("/api/orders/", headers=auth_headers)
        assert order_response.status_code == status.HTTP_201_CREATED
        
        # Verify order was created with correct quantity
        order = order_response.json()
        assert order["items"][0]["quantity"] == 2


@pytest.mark.integration
class TestPaymentOrderIntegration:
    """Test payment processing with order creation"""
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_payment_failure_preserves_cart(self, mock_create, mock_retrieve, client, auth_headers, sample_products):
        """Test failed payment keeps cart intact for retry"""
        # Add items to cart
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 2})
        
        # Get cart state
        initial_cart = client.get("/api/cart/", headers=auth_headers).json()
        initial_items = len(initial_cart["items"])
        
        # Create checkout session
        mock_create.return_value = MagicMock(
            id='cs_fail_test',
            url='https://checkout.stripe.com/test',
            expires_at=1234567890
        )
        checkout_response = client.post("/api/payment/create-checkout-session", headers=auth_headers, json={})
        session_id = checkout_response.json()["checkout_session_id"]
        
        # Simulate payment cancellation
        mock_retrieve.return_value = MagicMock(id=session_id, payment_status='unpaid')
        client.post(f"/api/payment/cancel/{session_id}", headers=auth_headers)
        
        # Verify cart still has items
        final_cart = client.get("/api/cart/", headers=auth_headers).json()
        assert len(final_cart["items"]) == initial_items
        
        # Verify no orders were created
        orders = client.get("/api/orders/", headers=auth_headers).json()
        assert len(orders) == 0
    
    @patch('services.stripe_service.stripe.checkout.Session.retrieve')
    @patch('services.stripe_service.stripe.checkout.Session.create')
    def test_duplicate_payment_webhook_idempotent(self, mock_create, mock_retrieve, client, auth_headers, sample_products, test_user):
        """Test processing same payment webhook twice doesn't create duplicate orders"""
        # Setup cart
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 1})
        
        # Create checkout
        mock_create.return_value = MagicMock(id='cs_idempotent_test', url='https://checkout.stripe.com/test', expires_at=1234567890)
        checkout_response = client.post("/api/payment/create-checkout-session", headers=auth_headers, json={})
        session_id = checkout_response.json()["checkout_session_id"]
        
        # Mock successful payment
        mock_retrieve.return_value = MagicMock(
            id=session_id,
            payment_status='paid',
            amount_total=99999,
            metadata={'user_id': str(test_user.id), 'cart_id': '1'}
        )
        
        # Process payment success first time
        response1 = client.post(f"/api/payment/success/{session_id}", headers=auth_headers)
        order1_id = response1.json()["order_id"]
        
        # Recreate cart (user added more items)
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 2, "quantity": 1})
        
        # Process same payment success again (duplicate webhook)
        response2 = client.post(f"/api/payment/success/{session_id}", headers=auth_headers)
        order2_id = response2.json()["order_id"]
        
        # Should return same order, not create duplicate
        assert order1_id == order2_id
        
        # Verify only one order exists
        orders = client.get("/api/orders/", headers=auth_headers).json()
        order_ids = [o["id"] for o in orders]
        assert order_ids.count(order1_id) == 1


@pytest.mark.integration
class TestAdminWorkflows:
    """Test admin management workflows"""
    
    def test_admin_view_all_orders_workflow(self, client, auth_headers, admin_headers, sample_products):
        """Test admin can view and manage all customer orders"""
        # Customer 1 places order
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 1})
        customer_order = client.post("/api/orders/", headers=auth_headers).json()
        
        # Admin places own order
        client.post("/api/cart/items", headers=admin_headers, json={"product_id": 2, "quantity": 1})
        admin_order = client.post("/api/orders/", headers=admin_headers).json()
        
        # Admin views all orders
        all_orders = client.get("/api/orders/admin/all", headers=admin_headers).json()
        assert len(all_orders) >= 2
        
        order_ids = [o["id"] for o in all_orders]
        assert customer_order["id"] in order_ids
        assert admin_order["id"] in order_ids
        
        # Admin can access customer's order directly
        customer_order_detail = client.get(
            f"/api/orders/admin/{customer_order['id']}",
            headers=admin_headers
        ).json()
        assert customer_order_detail["id"] == customer_order["id"]
    
    def test_admin_product_management_workflow(self, client, admin_headers, sample_products):
        """Test admin can manage product catalog"""
        # Create new product
        new_product = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "New Product",
                "price": 299.99,
                "brand": "TestBrand",
                "category": "Electronics",
                "stock": 100
            }
        ).json()
        
        # Update product
        updated = client.put(
            f"/api/products/{new_product['id']}",
            headers=admin_headers,
            json={"price": 249.99, "stock": 150}
        ).json()
        assert updated["price"] == 249.99
        assert updated["stock"] == 150
        
        # Verify product appears in catalog
        all_products = client.get("/api/products/").json()
        product_ids = [p["id"] for p in all_products]
        assert new_product["id"] in product_ids
        
        # Delete product
        delete_response = client.delete(
            f"/api/products/{new_product['id']}",
            headers=admin_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify product is removed
        get_response = client.get(f"/api/products/{new_product['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test authentication across multiple requests"""
    
    def test_token_persists_across_requests(self, client, sample_products):
        """Test authentication token works across multiple API calls"""
        # Register
        client.post(
            "/api/auth/register",
            json={"name": "Token Test", "email": "token@test.com", "password": "pass123"}
        )
        
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "token@test.com", "password": "pass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Use token for multiple operations
        # 1. Get profile
        profile = client.get("/api/auth/me", headers=headers)
        assert profile.status_code == status.HTTP_200_OK
        
        # 2. Add to cart
        cart_add = client.post("/api/cart/items", headers=headers, json={"product_id": 1, "quantity": 1})
        assert cart_add.status_code == status.HTTP_201_CREATED
        
        # 3. View cart
        cart_view = client.get("/api/cart/", headers=headers)
        assert cart_view.status_code == status.HTTP_200_OK
        
        # 4. Place order
        order = client.post("/api/orders/", headers=headers)
        assert order.status_code == status.HTTP_201_CREATED
        
        # 5. View orders
        orders = client.get("/api/orders/", headers=headers)
        assert orders.status_code == status.HTTP_200_OK
    
    def test_invalid_token_rejected_consistently(self, client, sample_products):
        """Test invalid token is rejected across all protected endpoints"""
        bad_headers = {"Authorization": "Bearer invalid_token_xyz"}
        
        # All protected endpoints should reject
        endpoints = [
            ("get", "/api/auth/me"),
            ("get", "/api/cart/"),
            ("post", "/api/cart/items"),
            ("get", "/api/orders/"),
            ("post", "/api/orders/"),
        ]
        
        for method, endpoint in endpoints:
            if method == "get":
                response = client.get(endpoint, headers=bad_headers)
            else:
                response = client.post(endpoint, headers=bad_headers, json={})
            
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.integration
class TestDatabaseTransactionIntegrity:
    """Test database transaction rollback and consistency"""
    
    def test_order_creation_atomic(self, client, auth_headers, sample_products):
        """Test order creation is atomic - all or nothing"""
        # Add items to cart
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 2})
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": 2, "quantity": 1})
        
        # Place order
        order_response = client.post("/api/orders/", headers=auth_headers)
        assert order_response.status_code == status.HTTP_201_CREATED
        
        order = order_response.json()
        
        # Verify order has all items
        assert len(order["items"]) == 2
        
        # Verify cart is completely cleared (not partial)
        cart = client.get("/api/cart/", headers=auth_headers).json()
        assert len(cart["items"]) == 0
        
        # Verify order total matches sum of items
        items_total = sum(item["total_amount"] for item in order["items"])
        assert abs(order["total_amount"] - items_total) < 0.01
    
    def test_cart_operations_consistent(self, client, auth_headers, sample_products):
        """Test cart operations maintain consistency"""
        # Add same product multiple times
        for _ in range(3):
            client.post("/api/cart/items", headers=auth_headers, json={"product_id": 1, "quantity": 1})
        
        # Should have single item with quantity 3, not 3 separate items
        cart = client.get("/api/cart/", headers=auth_headers).json()
        assert len(cart["items"]) == 1
        assert cart["items"][0]["quantity"] == 3
        
        # Total should reflect accumulated quantity
        expected_total = 999.99 * 3  # iPhone price * quantity
        assert abs(cart["total_price"] - expected_total) < 0.01


@pytest.mark.integration
class TestProductCatalogIntegration:
    """Test product catalog interactions with cart and orders"""
    
    def test_product_filtering_with_cart_operations(self, client, auth_headers, sample_products):
        """Test filtering products and adding filtered results to cart"""
        # Filter by brand
        apple_products = client.get("/api/products/brand/Apple").json()
        assert len(apple_products) > 0
        
        # Add filtered product to cart
        apple_product_id = apple_products[0]["id"]
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": apple_product_id, "quantity": 1})
        
        # Filter by category
        smartphone_products = client.get("/api/products/category/Smartphone").json()
        assert len(smartphone_products) >= 3
        
        # Add another filtered product
        samsung_product = next(p for p in smartphone_products if p["brand"] == "Samsung")
        client.post("/api/cart/items", headers=auth_headers, json={"product_id": samsung_product["id"], "quantity": 1})
        
        # Verify cart has products from both filters
        cart = client.get("/api/cart/", headers=auth_headers).json()
        assert len(cart["items"]) == 2
        
        brands = [item["product"]["brand"] for item in cart["items"]]
        assert "Apple" in brands
        assert "Samsung" in brands
