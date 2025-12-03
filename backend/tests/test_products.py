"""
Product Endpoint Tests

This module tests all product-related endpoints:
- GET /api/products/ - Get all products
- GET /api/products/{product_id} - Get product by ID
- GET /api/products/brand/{brand_name} - Get products by brand
- GET /api/products/category/{category_name} - Get products by category
- POST /api/products/ - Create product (Admin only)
- PUT /api/products/{product_id} - Update product (Admin only)
- DELETE /api/products/{product_id} - Delete product (Admin only)

Test Coverage:
- Public endpoints (GET requests) work without authentication
- Admin-only endpoints require authentication and admin role
- Proper validation of product data
- Error handling for not found resources
- Brand and category filtering (case-insensitive)
"""

from fastapi import status


class TestGetProducts:
    """Test cases for retrieving products"""
    
    def test_get_all_products_empty(self, client):
        """Test getting all products when database is empty"""
        response = client.get("/api/products/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_products_with_data(self, client, sample_products):
        """Test getting all products when products exist"""
        response = client.get("/api/products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "iPhone 15 Pro"
        assert data[1]["name"] == "Samsung Galaxy S24"
        assert data[2]["name"] == "Google Pixel 8"
    
    def test_get_product_by_id_success(self, client, sample_products):
        """Test getting a specific product by ID"""
        response = client.get("/api/products/1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "iPhone 15 Pro"
        assert data["brand"] == "Apple"
        assert data["price"] == 999.99
    
    def test_get_product_by_id_not_found(self, client):
        """Test getting a non-existent product"""
        response = client.get("/api/products/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_product_invalid_id(self, client):
        """Test getting a product with invalid ID format"""
        response = client.get("/api/products/invalid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProductsByBrand:
    """Test cases for brand filtering"""
    
    def test_get_products_by_brand_success(self, client, sample_products):
        """Test getting products by brand name"""
        response = client.get("/api/products/brand/Apple")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand"] == "Apple"
        assert data[0]["name"] == "iPhone 15 Pro"
    
    def test_get_products_by_brand_case_insensitive(self, client, sample_products):
        """Test brand filtering is case-insensitive"""
        response = client.get("/api/products/brand/APPLE")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand"] == "Apple"
    
    def test_get_products_by_brand_partial_match(self, client, sample_products):
        """Test brand filtering supports partial matches"""
        response = client.get("/api/products/brand/Sam")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand"] == "Samsung"
    
    def test_get_products_by_brand_not_found(self, client, sample_products):
        """Test getting products by non-existent brand"""
        response = client.get("/api/products/brand/NonExistentBrand")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "brand" in response.json()["detail"].lower()


class TestProductsByCategory:
    """Test cases for category filtering"""
    
    def test_get_products_by_category_success(self, client, sample_products):
        """Test getting products by category"""
        response = client.get("/api/products/category/Smartphone")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # All test products are smartphones
        assert all(p["category"] == "Smartphone" for p in data)
    
    def test_get_products_by_category_case_insensitive(self, client, sample_products):
        """Test category filtering is case-insensitive"""
        response = client.get("/api/products/category/SMARTPHONE")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
    
    def test_get_products_by_category_not_found(self, client, sample_products):
        """Test getting products by non-existent category"""
        response = client.get("/api/products/category/NonExistentCategory")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "category" in response.json()["detail"].lower()


class TestCreateProduct:
    """Test cases for creating products"""
    
    def test_create_product_without_auth(self, client):
        """Test creating product without authentication fails"""
        response = client.post(
            "/api/products/",
            json={
                "name": "New Product",
                "price": 599.99,
                "brand": "TestBrand",
                "category": "TestCategory",
                "stock": 100
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_product_as_customer(self, client, auth_headers):
        """Test creating product as non-admin user fails"""
        response = client.post(
            "/api/products/",
            headers=auth_headers,
            json={
                "name": "New Product",
                "price": 599.99,
                "brand": "TestBrand",
                "category": "TestCategory",
                "stock": 100
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_product_as_admin_success(self, client, admin_headers):
        """Test admin can successfully create a product"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "New iPhone",
                "price": 1299.99,
                "description": "Latest flagship phone",
                "brand": "Apple",
                "category": "Smartphone",
                "stock": 50
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New iPhone"
        assert data["price"] == 1299.99
        assert data["brand"] == "Apple"
        assert data["stock"] == 50
        assert "id" in data
        assert data["rating"] == 0.0  # Default rating
        assert data["ratings"] == 0  # Default ratings count
    
    def test_create_product_minimal_data(self, client, admin_headers):
        """Test creating product with only required fields"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "Minimal Product",
                "price": 99.99
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Minimal Product"
        assert data["price"] == 99.99
        assert data["description"] is None
        assert data["brand"] is None
    
    def test_create_product_missing_name(self, client, admin_headers):
        """Test creating product without name fails"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "price": 99.99
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_product_missing_price(self, client, admin_headers):
        """Test creating product without price fails"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "No Price Product"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_product_invalid_price(self, client, admin_headers):
        """Test creating product with invalid price type"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "Invalid Price",
                "price": "not-a-number"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_product_negative_price(self, client, admin_headers):
        """Test creating product with negative price (currently allowed)"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "Negative Price",
                "price": -50.0
            }
        )
        
        # Note: Schema allows negative prices - consider adding gt=0 validation
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["price"] == -50.0


class TestUpdateProduct:
    """Test cases for updating products"""
    
    def test_update_product_without_auth(self, client, sample_products):
        """Test updating product without authentication fails"""
        response = client.put(
            "/api/products/1",
            json={"price": 899.99}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_product_as_customer(self, client, auth_headers, sample_products):
        """Test updating product as non-admin user fails"""
        response = client.put(
            "/api/products/1",
            headers=auth_headers,
            json={"price": 899.99}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_product_as_admin_success(self, client, admin_headers, sample_products):
        """Test admin can successfully update a product"""
        response = client.put(
            "/api/products/1",
            headers=admin_headers,
            json={
                "price": 899.99,
                "stock": 75
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["price"] == 899.99
        assert data["stock"] == 75
        assert data["name"] == "iPhone 15 Pro"  # Unchanged fields remain
    
    def test_update_product_partial_update(self, client, admin_headers, sample_products):
        """Test updating only specific fields"""
        response = client.put(
            "/api/products/2",
            headers=admin_headers,
            json={"description": "Updated description"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["name"] == "Samsung Galaxy S24"  # Other fields unchanged
        assert data["price"] == 899.99
    
    def test_update_product_not_found(self, client, admin_headers):
        """Test updating non-existent product"""
        response = client.put(
            "/api/products/99999",
            headers=admin_headers,
            json={"price": 999.99}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_product_all_fields(self, client, admin_headers, sample_products):
        """Test updating all product fields"""
        response = client.put(
            "/api/products/1",
            headers=admin_headers,
            json={
                "name": "iPhone 16 Pro",
                "price": 1099.99,
                "description": "Next generation",
                "brand": "Apple",
                "stock": 100,
                "category": "Premium Smartphone",
                "picture": "iphone16.jpg"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "iPhone 16 Pro"
        assert data["price"] == 1099.99
        assert data["category"] == "Premium Smartphone"


class TestDeleteProduct:
    """Test cases for deleting products"""
    
    def test_delete_product_without_auth(self, client, sample_products):
        """Test deleting product without authentication fails"""
        response = client.delete("/api/products/1")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_product_as_customer(self, client, auth_headers, sample_products):
        """Test deleting product as non-admin user fails"""
        response = client.delete(
            "/api/products/1",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_product_as_admin_success(self, client, admin_headers, sample_products):
        """Test admin can successfully delete a product"""
        response = client.delete(
            "/api/products/1",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify product is deleted
        get_response = client.get("/api/products/1")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_product_not_found(self, client, admin_headers):
        """Test deleting non-existent product"""
        response = client.delete(
            "/api/products/99999",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_product_verify_list_updated(self, client, admin_headers, sample_products):
        """Test that product list is updated after deletion"""
        # Get initial count
        list_response = client.get("/api/products/")
        initial_count = len(list_response.json())
        
        # Delete a product
        client.delete("/api/products/2", headers=admin_headers)
        
        # Verify count decreased
        list_response = client.get("/api/products/")
        assert len(list_response.json()) == initial_count - 1
        
        # Verify deleted product not in list
        products = list_response.json()
        assert all(p["id"] != 2 for p in products)


class TestProductDataValidation:
    """Test product data validation and edge cases"""
    
    def test_product_response_structure(self, client, sample_products):
        """Test that product response has all expected fields"""
        response = client.get("/api/products/1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Required fields
        assert "id" in data
        assert "name" in data
        assert "price" in data
        
        # Optional fields (should be present, may be null)
        assert "description" in data
        assert "brand" in data
        assert "rating" in data
        assert "ratings" in data
        assert "stock" in data
        assert "category" in data
        assert "picture" in data
    
    def test_product_price_precision(self, client, admin_headers):
        """Test product price decimal precision"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "Precision Test",
                "price": 123.456789  # High precision
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        # Price should maintain reasonable precision
        data = response.json()
        assert isinstance(data["price"], float)
    
    def test_product_stock_zero(self, client, admin_headers):
        """Test creating product with zero stock"""
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "Out of Stock",
                "price": 99.99,
                "stock": 0
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["stock"] == 0
    
    def test_product_long_description(self, client, admin_headers):
        """Test product with very long description"""
        long_description = "A" * 5000  # 5000 character description
        
        response = client.post(
            "/api/products/",
            headers=admin_headers,
            json={
                "name": "Long Description Product",
                "price": 99.99,
                "description": long_description
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()["description"]) == 5000
