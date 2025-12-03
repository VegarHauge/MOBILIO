"""
Order Endpoint Tests

This module tests all order-related endpoints:
- POST /api/orders/ - Place order from cart
- GET /api/orders/ - Get user's orders
- GET /api/orders/{order_id} - Get specific order (user's own)
- GET /api/orders/admin/all - Get all orders (Admin only)
- GET /api/orders/admin/{order_id} - Get any order (Admin only)

Test Coverage:
- Order creation from cart
- Cart clearing after order placement
- User can only access own orders
- Admin can access all orders
- Order item details and totals
- Empty cart handling
- Authentication and authorization
- Order history ordering
"""

from fastapi import status


class TestPlaceOrder:
    """Test cases for placing orders from cart"""
    
    def test_place_order_without_auth(self, client, cart_with_items):
        """Test placing order without authentication fails"""
        response = client.post("/api/orders/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_place_order_from_cart_success(self, client, auth_headers, cart_with_items):
        """Test successfully placing order from cart"""
        response = client.post("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify order structure
        assert "id" in data
        assert "customer_id" in data
        assert "total_amount" in data
        assert "created_at" in data
        assert "items" in data
        
        # Verify order has items from cart
        assert len(data["items"]) == 2  # cart_with_items has 2 items
        
        # Verify total amount is calculated correctly
        expected_total = (999.99 * 2) + (899.99 * 1)  # iPhone x2 + Samsung x1
        assert abs(data["total_amount"] - expected_total) < 0.01
    
    def test_place_order_clears_cart(self, client, auth_headers, cart_with_items):
        """Test that placing order clears the user's cart"""
        # Place order
        response = client.post("/api/orders/", headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify cart is now empty
        cart_response = client.get("/api/cart/", headers=auth_headers)
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 0
        assert cart_data["total_price"] == 0.0
    
    def test_place_order_from_empty_cart(self, client, auth_headers):
        """Test placing order with empty cart fails"""
        response = client.post("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.json()["detail"].lower()
    
    def test_place_order_items_structure(self, client, auth_headers, cart_with_items):
        """Test order items have correct structure and data"""
        response = client.post("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        order_items = response.json()["items"]
        
        for item in order_items:
            assert "id" in item
            assert "product_id" in item
            assert "quantity" in item
            assert "total_amount" in item
            assert "product" in item
            
            # Verify product details are included
            product = item["product"]
            assert "id" in product
            assert "name" in product
            assert "price" in product
    
    def test_place_order_total_calculation(self, client, auth_headers, cart_with_items):
        """Test order total matches sum of order items"""
        response = client.post("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Calculate total from items
        items_total = sum(item["total_amount"] for item in data["items"])
        
        # Should match order total
        assert abs(data["total_amount"] - items_total) < 0.01
    
    def test_place_multiple_orders(self, client, auth_headers, sample_products):
        """Test user can place multiple orders"""
        # Place first order
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        response1 = client.post("/api/orders/", headers=auth_headers)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Add items to cart again and place second order
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 2, "quantity": 1}
        )
        response2 = client.post("/api/orders/", headers=auth_headers)
        assert response2.status_code == status.HTTP_201_CREATED
        
        # Verify different order IDs
        assert response1.json()["id"] != response2.json()["id"]
    
    def test_place_order_preserves_product_info(self, client, auth_headers, sample_products):
        """Test order items preserve product information at time of purchase"""
        # Add product to cart
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        # Place order
        response = client.post("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        order_item = response.json()["items"][0]
        
        # Verify product details are preserved
        assert order_item["product"]["name"] == "iPhone 15 Pro"
        assert order_item["product"]["brand"] == "Apple"
        assert order_item["total_amount"] == 999.99  # Price at time of order


class TestGetUserOrders:
    """Test cases for retrieving user's orders"""
    
    def test_get_orders_without_auth(self, client):
        """Test getting orders without authentication fails"""
        response = client.get("/api/orders/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_orders_empty_list(self, client, auth_headers):
        """Test getting orders when user has no orders"""
        response = client.get("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_orders_with_orders(self, client, auth_headers, placed_order):
        """Test getting orders when user has orders"""
        response = client.get("/api/orders/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        assert len(orders) == 1
        assert orders[0]["id"] == placed_order.id
    
    def test_get_orders_multiple_orders(self, client, auth_headers, sample_products):
        """Test getting multiple orders in correct order (newest first)"""
        # Create two orders
        for i in range(2):
            client.post(
                "/api/cart/items",
                headers=auth_headers,
                json={"product_id": i + 1, "quantity": 1}
            )
            client.post("/api/orders/", headers=auth_headers)
        
        response = client.get("/api/orders/", headers=auth_headers)
        orders = response.json()
        
        assert len(orders) == 2
        # Verify orders are sorted by created_at descending (newest first)
        assert orders[0]["id"] > orders[1]["id"]
    
    def test_get_orders_only_users_orders(self, client, auth_headers, admin_headers, sample_products):
        """Test user only sees their own orders, not other users' orders"""
        # User creates an order
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        client.post("/api/orders/", headers=auth_headers)
        
        # Admin creates an order
        client.post(
            "/api/cart/items",
            headers=admin_headers,
            json={"product_id": 2, "quantity": 1}
        )
        client.post("/api/orders/", headers=admin_headers)
        
        # User should only see their own order
        user_response = client.get("/api/orders/", headers=auth_headers)
        assert len(user_response.json()) == 1
        
        # Admin should only see their own order (when accessing user endpoint)
        admin_response = client.get("/api/orders/", headers=admin_headers)
        assert len(admin_response.json()) == 1
    
    def test_get_orders_includes_all_details(self, client, auth_headers, placed_order):
        """Test orders include all necessary details"""
        response = client.get("/api/orders/", headers=auth_headers)
        
        order = response.json()[0]
        assert "id" in order
        assert "customer_id" in order
        assert "total_amount" in order
        assert "created_at" in order
        assert "items" in order
        assert len(order["items"]) > 0


class TestGetOrderById:
    """Test cases for retrieving specific order by ID"""
    
    def test_get_order_without_auth(self, client, placed_order):
        """Test getting order without authentication fails"""
        response = client.get(f"/api/orders/{placed_order.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_order_by_id_success(self, client, auth_headers, placed_order):
        """Test successfully getting order by ID"""
        response = client.get(f"/api/orders/{placed_order.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == placed_order.id
        assert data["customer_id"] == placed_order.customer_id
        assert len(data["items"]) > 0
    
    def test_get_order_not_found(self, client, auth_headers):
        """Test getting non-existent order"""
        response = client.get("/api/orders/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_order_invalid_id(self, client, auth_headers):
        """Test getting order with invalid ID format"""
        response = client.get("/api/orders/invalid", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_another_users_order(self, client, auth_headers, admin_headers, sample_products):
        """Test user cannot access another user's order"""
        # Admin places an order
        client.post(
            "/api/cart/items",
            headers=admin_headers,
            json={"product_id": 1, "quantity": 1}
        )
        admin_order_response = client.post("/api/orders/", headers=admin_headers)
        admin_order_id = admin_order_response.json()["id"]
        
        # Regular user tries to access admin's order
        response = client.get(f"/api/orders/{admin_order_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_order_with_items(self, client, auth_headers, placed_order):
        """Test order includes all items with details"""
        response = client.get(f"/api/orders/{placed_order.id}", headers=auth_headers)
        
        data = response.json()
        items = data["items"]
        
        assert len(items) > 0
        for item in items:
            assert "id" in item
            assert "product_id" in item
            assert "quantity" in item
            assert "total_amount" in item
            assert "product" in item


class TestAdminGetAllOrders:
    """Test cases for admin retrieving all orders"""
    
    def test_admin_get_all_orders_without_auth(self, client):
        """Test getting all orders without authentication fails"""
        response = client.get("/api/orders/admin/all")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_get_all_orders_as_customer(self, client, auth_headers, placed_order):
        """Test non-admin user cannot access all orders"""
        response = client.get("/api/orders/admin/all", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_get_all_orders_success(self, client, admin_headers):
        """Test admin can get all orders"""
        response = client.get("/api/orders/admin/all", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_admin_get_all_orders_from_multiple_users(self, client, auth_headers, admin_headers, sample_products):
        """Test admin sees orders from all users"""
        # Customer places order
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        customer_order = client.post("/api/orders/", headers=auth_headers)
        customer_order_id = customer_order.json()["id"]
        
        # Admin places order
        client.post(
            "/api/cart/items",
            headers=admin_headers,
            json={"product_id": 2, "quantity": 1}
        )
        admin_order = client.post("/api/orders/", headers=admin_headers)
        admin_order_id = admin_order.json()["id"]
        
        # Admin retrieves all orders
        response = client.get("/api/orders/admin/all", headers=admin_headers)
        
        orders = response.json()
        assert len(orders) >= 2
        order_ids = [order["id"] for order in orders]
        assert customer_order_id in order_ids
        assert admin_order_id in order_ids
    
    def test_admin_get_all_orders_sorted_by_date(self, client, admin_headers, sample_products):
        """Test all orders are sorted by created_at descending"""
        # Create multiple orders
        for i in range(3):
            client.post(
                "/api/cart/items",
                headers=admin_headers,
                json={"product_id": (i % 3) + 1, "quantity": 1}
            )
            client.post("/api/orders/", headers=admin_headers)
        
        response = client.get("/api/orders/admin/all", headers=admin_headers)
        orders = response.json()
        
        # Verify newest orders come first
        for i in range(len(orders) - 1):
            assert orders[i]["id"] >= orders[i + 1]["id"]


class TestAdminGetOrderById:
    """Test cases for admin retrieving any order by ID"""
    
    def test_admin_get_order_without_auth(self, client, placed_order):
        """Test admin endpoint without authentication fails"""
        response = client.get(f"/api/orders/admin/{placed_order.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_get_order_as_customer(self, client, auth_headers, placed_order):
        """Test non-admin cannot use admin endpoint"""
        response = client.get(f"/api/orders/admin/{placed_order.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_get_order_success(self, client, admin_headers, placed_order):
        """Test admin can get any order by ID"""
        response = client.get(f"/api/orders/admin/{placed_order.id}", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == placed_order.id
    
    def test_admin_get_another_users_order(self, client, auth_headers, admin_headers, sample_products):
        """Test admin can access any user's order"""
        # Customer places order
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        customer_order = client.post("/api/orders/", headers=auth_headers)
        customer_order_id = customer_order.json()["id"]
        
        # Admin accesses customer's order
        response = client.get(
            f"/api/orders/admin/{customer_order_id}",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == customer_order_id
    
    def test_admin_get_order_not_found(self, client, admin_headers):
        """Test admin gets 404 for non-existent order"""
        response = client.get("/api/orders/admin/99999", headers=admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrderDataIntegrity:
    """Test order data integrity and business logic"""
    
    def test_order_timestamps(self, client, auth_headers, placed_order):
        """Test order has valid created_at timestamp"""
        response = client.get(f"/api/orders/{placed_order.id}", headers=auth_headers)
        
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None
    
    def test_order_item_quantities_preserved(self, client, auth_headers, sample_products):
        """Test order items preserve correct quantities from cart"""
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
        
        # Place order
        response = client.post("/api/orders/", headers=auth_headers)
        
        items = response.json()["items"]
        quantities = {item["product_id"]: item["quantity"] for item in items}
        
        assert quantities[1] == 5
        assert quantities[2] == 3
    
    def test_order_item_totals_calculated_correctly(self, client, auth_headers, sample_products):
        """Test each order item has correct total_amount"""
        # Add items with different quantities
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 3}  # iPhone 999.99 x3
        )
        
        response = client.post("/api/orders/", headers=auth_headers)
        
        items = response.json()["items"]
        iphone_item = next(i for i in items if i["product_id"] == 1)
        
        expected_total = 999.99 * 3
        assert abs(iphone_item["total_amount"] - expected_total) < 0.01
    
    def test_order_customer_id_matches_user(self, client, auth_headers, test_user, placed_order):
        """Test order is associated with correct customer"""
        response = client.get(f"/api/orders/{placed_order.id}", headers=auth_headers)
        
        data = response.json()
        assert data["customer_id"] == test_user.id
    
    def test_order_stripe_session_field(self, client, auth_headers, placed_order):
        """Test order has stripe_session_id field (even if null)"""
        response = client.get(f"/api/orders/{placed_order.id}", headers=auth_headers)
        
        data = response.json()
        # Field should be present in response (can be null)
        assert "stripe_session_id" in data
    
    def test_multiple_orders_independent(self, client, auth_headers, sample_products):
        """Test multiple orders are independent and don't affect each other"""
        # Place first order
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        order1 = client.post("/api/orders/", headers=auth_headers)
        order1_id = order1.json()["id"]
        order1_total = order1.json()["total_amount"]
        
        # Place second order with different items
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 2, "quantity": 2}
        )
        order2 = client.post("/api/orders/", headers=auth_headers)
        order2_id = order2.json()["id"]
        order2_total = order2.json()["total_amount"]
        
        # Verify orders are different
        assert order1_id != order2_id
        assert order1_total != order2_total
        
        # Verify first order unchanged
        verify_response = client.get(f"/api/orders/{order1_id}", headers=auth_headers)
        assert verify_response.json()["total_amount"] == order1_total
