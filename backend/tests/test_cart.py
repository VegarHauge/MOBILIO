"""
Cart Endpoint Tests

This module tests all cart-related endpoints:
- GET /api/cart/ - Get user's cart
- POST /api/cart/items - Add item to cart
- PUT /api/cart/items/{cart_item_id} - Update cart item quantity
- DELETE /api/cart/items/{cart_item_id} - Remove item from cart
- PATCH /api/cart/items/{cart_item_id}/increment - Increment quantity
- PATCH /api/cart/items/{cart_item_id}/decrement - Decrement quantity

Test Coverage:
- All endpoints require authentication
- Cart creation and retrieval
- Adding items (new and existing)
- Quantity updates
- Item removal
- Cart total calculation
- Edge cases (invalid products, quantities)
"""

from fastapi import status


class TestGetCart:
    """Test cases for retrieving cart"""
    
    def test_get_cart_without_auth(self, client):
        """Test getting cart without authentication fails"""
        response = client.get("/api/cart/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_empty_cart(self, client, auth_headers):
        """Test getting cart when user has no cart (creates empty cart)"""
        response = client.get("/api/cart/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["items"] == []
        assert data["total_price"] == 0.0
    
    def test_get_cart_with_items(self, client, auth_headers, cart_with_items):
        """Test getting cart with items"""
        response = client.get("/api/cart/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total_price"] > 0
        
        # Verify item structure
        item = data["items"][0]
        assert "id" in item
        assert "product_id" in item
        assert "quantity" in item
        assert "price" in item
        assert "product" in item  # Nested product details


class TestAddItemToCart:
    """Test cases for adding items to cart"""
    
    def test_add_item_without_auth(self, client, sample_products):
        """Test adding item without authentication fails"""
        response = client.post(
            "/api/cart/items",
            json={"product_id": 1, "quantity": 1}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_add_item_to_cart_success(self, client, auth_headers, sample_products):
        """Test successfully adding item to cart"""
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == 1
        assert data["quantity"] == 2
        assert data["price"] == 999.99  # iPhone price
        assert "id" in data
    
    def test_add_item_default_quantity(self, client, auth_headers, sample_products):
        """Test adding item with default quantity (1)"""
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 2}  # No quantity specified
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["quantity"] == 1
    
    def test_add_same_item_updates_quantity(self, client, auth_headers, sample_products):
        """Test adding same item twice increases quantity"""
        # Add item first time
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        # Add same item again
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 3}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["quantity"] == 5  # 2 + 3
    
    def test_add_nonexistent_product(self, client, auth_headers):
        """Test adding non-existent product to cart"""
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 99999, "quantity": 1}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_add_item_missing_product_id(self, client, auth_headers):
        """Test adding item without product_id"""
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"quantity": 1}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_item_invalid_quantity_type(self, client, auth_headers, sample_products):
        """Test adding item with invalid quantity type"""
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": "invalid"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_multiple_different_products(self, client, auth_headers, sample_products):
        """Test adding multiple different products"""
        # Add first product
        response1 = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Add second product
        response2 = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 2, "quantity": 2}
        )
        assert response2.status_code == status.HTTP_201_CREATED
        
        # Verify cart has both items
        cart_response = client.get("/api/cart/", headers=auth_headers)
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 2


class TestUpdateCartItem:
    """Test cases for updating cart item quantities"""
    
    def test_update_cart_item_without_auth(self, client, cart_with_items):
        """Test updating cart item without authentication fails"""
        cart_item_id = cart_with_items[0].id
        response = client.put(
            f"/api/cart/items/{cart_item_id}",
            json={"quantity": 5}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_cart_item_quantity_success(self, client, auth_headers, cart_with_items):
        """Test successfully updating cart item quantity"""
        cart_item_id = cart_with_items[0].id
        response = client.put(
            f"/api/cart/items/{cart_item_id}",
            headers=auth_headers,
            json={"quantity": 5}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == cart_item_id
        assert data["quantity"] == 5
    
    def test_update_cart_item_quantity_to_zero_removes(self, client, auth_headers, cart_with_items):
        """Test updating quantity to zero removes the item"""
        cart_item_id = cart_with_items[0].id
        response = client.put(
            f"/api/cart/items/{cart_item_id}",
            headers=auth_headers,
            json={"quantity": 0}
        )
        
        # Returns 404 because item is removed
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_nonexistent_cart_item(self, client, auth_headers):
        """Test updating non-existent cart item"""
        response = client.put(
            "/api/cart/items/99999",
            headers=auth_headers,
            json={"quantity": 5}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_another_users_cart_item(self, client, auth_headers, admin_headers, cart_with_items):
        """Test user cannot update another user's cart item"""
        cart_item_id = cart_with_items[0].id  # Belongs to test_user
        
        # Try to update with admin's token
        response = client.put(
            f"/api/cart/items/{cart_item_id}",
            headers=admin_headers,
            json={"quantity": 10}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_cart_item_missing_quantity(self, client, auth_headers, cart_with_items):
        """Test updating cart item without quantity field"""
        cart_item_id = cart_with_items[0].id
        response = client.put(
            f"/api/cart/items/{cart_item_id}",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRemoveCartItem:
    """Test cases for removing items from cart"""
    
    def test_remove_cart_item_without_auth(self, client, cart_with_items):
        """Test removing cart item without authentication fails"""
        cart_item_id = cart_with_items[0].id
        response = client.delete(f"/api/cart/items/{cart_item_id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_remove_cart_item_success(self, client, auth_headers, cart_with_items):
        """Test successfully removing cart item"""
        cart_item_id = cart_with_items[0].id
        response = client.delete(
            f"/api/cart/items/{cart_item_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify item is removed
        cart_response = client.get("/api/cart/", headers=auth_headers)
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 1  # Started with 2, removed 1
        assert all(item["id"] != cart_item_id for item in cart_data["items"])
    
    def test_remove_nonexistent_cart_item(self, client, auth_headers):
        """Test removing non-existent cart item"""
        response = client.delete(
            "/api/cart/items/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_remove_another_users_cart_item(self, client, auth_headers, admin_headers, cart_with_items):
        """Test user cannot remove another user's cart item"""
        cart_item_id = cart_with_items[0].id
        
        response = client.delete(
            f"/api/cart/items/{cart_item_id}",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIncrementCartItem:
    """Test cases for incrementing cart item quantity"""
    
    def test_increment_without_auth(self, client, cart_with_items):
        """Test incrementing without authentication fails"""
        cart_item_id = cart_with_items[0].id
        response = client.patch(f"/api/cart/items/{cart_item_id}/increment")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_increment_cart_item_success(self, client, auth_headers, cart_with_items):
        """Test successfully incrementing cart item quantity"""
        cart_item_id = cart_with_items[0].id
        initial_quantity = cart_with_items[0].quantity
        
        response = client.patch(
            f"/api/cart/items/{cart_item_id}/increment",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == initial_quantity + 1
    
    def test_increment_multiple_times(self, client, auth_headers, cart_with_items):
        """Test incrementing multiple times"""
        cart_item_id = cart_with_items[0].id
        initial_quantity = cart_with_items[0].quantity
        
        # Increment 3 times
        for _ in range(3):
            client.patch(
                f"/api/cart/items/{cart_item_id}/increment",
                headers=auth_headers
            )
        
        # Verify final quantity
        cart_response = client.get("/api/cart/", headers=auth_headers)
        items = cart_response.json()["items"]
        item = next(i for i in items if i["id"] == cart_item_id)
        assert item["quantity"] == initial_quantity + 3
    
    def test_increment_nonexistent_cart_item(self, client, auth_headers):
        """Test incrementing non-existent cart item"""
        response = client.patch(
            "/api/cart/items/99999/increment",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDecrementCartItem:
    """Test cases for decrementing cart item quantity"""
    
    def test_decrement_without_auth(self, client, cart_with_items):
        """Test decrementing without authentication fails"""
        cart_item_id = cart_with_items[0].id
        response = client.patch(f"/api/cart/items/{cart_item_id}/decrement")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_decrement_cart_item_success(self, client, auth_headers, cart_with_items):
        """Test successfully decrementing cart item quantity"""
        cart_item_id = cart_with_items[0].id
        initial_quantity = cart_with_items[0].quantity
        
        response = client.patch(
            f"/api/cart/items/{cart_item_id}/decrement",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == initial_quantity - 1
    
    def test_decrement_to_zero_removes_item(self, client, auth_headers, sample_products):
        """Test decrementing quantity to zero removes item"""
        # Add item with quantity 1
        add_response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        cart_item_id = add_response.json()["id"]
        
        # Decrement (should remove)
        response = client.patch(
            f"/api/cart/items/{cart_item_id}/decrement",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "removed" in response.json()["detail"].lower()
    
    def test_decrement_nonexistent_cart_item(self, client, auth_headers):
        """Test decrementing non-existent cart item"""
        response = client.patch(
            "/api/cart/items/99999/decrement",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCartTotalCalculation:
    """Test cart total price calculation"""
    
    def test_empty_cart_total_zero(self, client, auth_headers):
        """Test empty cart has total of zero"""
        response = client.get("/api/cart/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_price"] == 0.0
    
    def test_cart_total_single_item(self, client, auth_headers, sample_products):
        """Test cart total with single item"""
        # Add iPhone (999.99) with quantity 2
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        response = client.get("/api/cart/", headers=auth_headers)
        data = response.json()
        
        expected_total = 999.99 * 2
        assert abs(data["total_price"] - expected_total) < 0.01
    
    def test_cart_total_multiple_items(self, client, auth_headers, sample_products):
        """Test cart total with multiple items"""
        # Add iPhone (999.99) x2
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 2}
        )
        
        # Add Samsung (899.99) x1
        client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 2, "quantity": 1}
        )
        
        response = client.get("/api/cart/", headers=auth_headers)
        data = response.json()
        
        expected_total = (999.99 * 2) + (899.99 * 1)
        assert abs(data["total_price"] - expected_total) < 0.01
    
    def test_cart_total_updates_after_quantity_change(self, client, auth_headers, cart_with_items):
        """Test cart total updates when quantity changes"""
        cart_item_id = cart_with_items[0].id
        
        # Get initial total
        initial_response = client.get("/api/cart/", headers=auth_headers)
        initial_total = initial_response.json()["total_price"]
        
        # Update quantity
        client.put(
            f"/api/cart/items/{cart_item_id}",
            headers=auth_headers,
            json={"quantity": 10}
        )
        
        # Get new total
        updated_response = client.get("/api/cart/", headers=auth_headers)
        updated_total = updated_response.json()["total_price"]
        
        assert updated_total != initial_total
        assert updated_total > initial_total


class TestCartItemProduct:
    """Test product details in cart items"""
    
    def test_cart_item_includes_product_details(self, client, auth_headers, cart_with_items):
        """Test cart item response includes full product details"""
        response = client.get("/api/cart/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        assert len(items) > 0
        
        item = items[0]
        product = item["product"]
        
        # Verify product details are included
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "brand" in product
        assert "category" in product
    
    def test_cart_item_price_matches_product_price(self, client, auth_headers, sample_products):
        """Test cart item stores correct product price"""
        # Add product
        response = client.post(
            "/api/cart/items",
            headers=auth_headers,
            json={"product_id": 1, "quantity": 1}
        )
        
        cart_item = response.json()
        
        # Verify stored price matches product price
        assert cart_item["price"] == 999.99  # iPhone price
        assert cart_item["product"]["price"] == 999.99
