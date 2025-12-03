"""
Pytest Configuration and Fixtures

This module provides shared fixtures for all tests including:
- Test database setup and teardown
- Test client configuration
- Authentication fixtures
- Mock data generators
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.base import Base
from db.deps import get_db
from models.user import User
from services.auth_service import AuthService

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test customer user"""
    hashed_password = AuthService.get_password_hash("testpassword123")
    user = User(
        name="Test User",
        email="test@example.com",
        password=hashed_password,
        role="customer"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user"""
    hashed_password = AuthService.get_password_hash("adminpass123")
    admin = User(
        name="Test Admin",
        email="admin@example.com",
        password=hashed_password,
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_token(test_user):
    """Generate an authentication token for test user"""
    from datetime import timedelta
    token = AuthService.create_access_token(
        data={
            "sub": str(test_user.id),
            "name": test_user.name,
            "email": test_user.email,
            "role": test_user.role
        },
        expires_delta=timedelta(minutes=30)
    )
    return token


@pytest.fixture
def admin_token(test_admin):
    """Generate an authentication token for admin user"""
    from datetime import timedelta
    token = AuthService.create_access_token(
        data={
            "sub": str(test_admin.id),
            "name": test_admin.name,
            "email": test_admin.email,
            "role": test_admin.role
        },
        expires_delta=timedelta(minutes=30)
    )
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Generate authorization headers with bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Generate authorization headers for admin"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_products(db_session):
    """Create sample products for testing"""
    from models.product import Product
    
    products = [
        Product(
            name="iPhone 15 Pro",
            price=999.99,
            description="Apple's flagship smartphone",
            brand="Apple",
            category="Smartphone",
            stock=50,
            rating=4.5,
            ratings=120
        ),
        Product(
            name="Samsung Galaxy S24",
            price=899.99,
            description="Samsung's latest flagship",
            brand="Samsung",
            category="Smartphone",
            stock=75,
            rating=4.3,
            ratings=95
        ),
        Product(
            name="Google Pixel 8",
            price=699.99,
            description="Google's pure Android experience",
            brand="Google",
            category="Smartphone",
            stock=40,
            rating=4.4,
            ratings=78
        )
    ]
    
    for product in products:
        db_session.add(product)
    db_session.commit()
    
    for product in products:
        db_session.refresh(product)
    
    return products


@pytest.fixture
def cart_with_items(db_session, test_user, sample_products):
    """Create a cart with items for testing"""
    from models.cart import Cart
    from models.cartitem import CartItem
    
    # Create cart for test user
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    
    # Add two items to cart
    cart_items = [
        CartItem(
            cart_id=cart.id,
            user_id=test_user.id,
            product_id=sample_products[0].id,  # iPhone
            quantity=2,
            price=sample_products[0].price
        ),
        CartItem(
            cart_id=cart.id,
            user_id=test_user.id,
            product_id=sample_products[1].id,  # Samsung
            quantity=1,
            price=sample_products[1].price
        )
    ]
    
    for item in cart_items:
        db_session.add(item)
    db_session.commit()
    
    for item in cart_items:
        db_session.refresh(item)
    
    return cart_items


@pytest.fixture
def placed_order(db_session, test_user, cart_with_items):
    """Create a placed order for testing"""
    from models.order import Order
    from models.orderitem import OrderItem
    from models.cart import Cart
    from datetime import datetime
    
    # Calculate total from cart items
    total_amount = sum(item.price * item.quantity for item in cart_with_items)
    
    # Create order
    order = Order(
        customer_id=test_user.id,
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    
    # Create order items from cart items
    for cart_item in cart_with_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            total_amount=cart_item.price * cart_item.quantity
        )
        db_session.add(order_item)
    
    db_session.commit()
    db_session.refresh(order)
    
    # Clear the cart items (simulating order placement)
    for cart_item in cart_with_items:
        db_session.delete(cart_item)
    
    # Delete the cart
    cart = db_session.query(Cart).filter(Cart.user_id == test_user.id).first()
    if cart:
        db_session.delete(cart)
    
    db_session.commit()
    
    return order
