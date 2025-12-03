from sqlalchemy.orm import Session
from models.cart import Cart
from models.cartitem import CartItem
from models.product import Product
from models.schemas import AddToCart, UpdateCartItem
from typing import Optional

class CartService:
    
    @staticmethod
    def get_or_create_user_cart(db: Session, user_id: int) -> Cart:
        """Get user's cart or create one if it doesn't exist"""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart
    
    @staticmethod
    def get_user_cart(db: Session, user_id: int) -> Optional[Cart]:
        """Get user's cart with all items"""
        return db.query(Cart).filter(Cart.user_id == user_id).first()
    
    @staticmethod
    def add_item_to_cart(db: Session, user_id: int, add_to_cart: AddToCart) -> CartItem:
        """Add item to cart or update quantity if item already exists"""
        # Get or create cart
        cart = CartService.get_or_create_user_cart(db, user_id)
        
        # Get product details
        product = db.query(Product).filter(Product.id == add_to_cart.product_id).first()
        if not product:
            raise ValueError(f"Product with id {add_to_cart.product_id} not found")
        
        # Check if item already exists in cart
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == add_to_cart.product_id
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += add_to_cart.quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                user_id=user_id,
                product_id=add_to_cart.product_id,
                quantity=add_to_cart.quantity,
                price=product.price
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def update_cart_item_quantity(db: Session, user_id: int, cart_item_id: int, update_data: UpdateCartItem) -> Optional[CartItem]:
        """Update quantity of a cart item"""
        cart_item = db.query(CartItem).filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id
        ).first()
        
        if not cart_item:
            return None
        
        if update_data.quantity <= 0:
            # Remove item if quantity is 0 or negative
            db.delete(cart_item)
            db.commit()
            return None
        else:
            cart_item.quantity = update_data.quantity
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def remove_item_from_cart(db: Session, user_id: int, cart_item_id: int) -> bool:
        """Remove an item from cart"""
        cart_item = db.query(CartItem).filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id
        ).first()
        
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        return True
    
    @staticmethod
    def increment_cart_item(db: Session, user_id: int, cart_item_id: int) -> Optional[CartItem]:
        """Increment cart item quantity by 1"""
        cart_item = db.query(CartItem).filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id
        ).first()
        
        if not cart_item:
            return None
        
        cart_item.quantity += 1
        db.commit()
        db.refresh(cart_item)
        return cart_item
    
    @staticmethod
    def decrement_cart_item(db: Session, user_id: int, cart_item_id: int) -> Optional[CartItem]:
        """Decrement cart item quantity by 1, remove if quantity becomes 0"""
        cart_item = db.query(CartItem).filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id
        ).first()
        
        if not cart_item:
            return None
        
        if cart_item.quantity <= 1:
            # Remove item if quantity would become 0
            db.delete(cart_item)
            db.commit()
            return None
        else:
            cart_item.quantity -= 1
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def calculate_cart_total(cart: Cart) -> float:
        """Calculate total price of all items in cart"""
        total = 0.0
        for item in cart.items:
            total += item.price * item.quantity
        return total
    
    @staticmethod
    def clear_user_cart(db: Session, user_id: int) -> bool:
        """Clear all items from user's cart"""
        cart = CartService.get_user_cart(db, user_id)
        if not cart:
            return False
        
        # Delete all cart items
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        return True