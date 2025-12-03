from sqlalchemy.orm import Session
from models.product import Product
from models.schemas import ProductCreate, ProductUpdate
from services.s3_service import s3_service
from fastapi import UploadFile
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ProductService:
    
    @staticmethod
    def get_all_products(db: Session) -> List[Product]:
        """Get all products from the database"""
        return db.query(Product).all()
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Get a product by its ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_products_by_brand(db: Session, brand_name: str) -> List[Product]:
        """Get all products by brand name (case-insensitive)"""
        return db.query(Product).filter(
            Product.brand.ilike(f"%{brand_name}%")
        ).all()
    
    @staticmethod
    def get_products_by_category(db: Session, category_name: str) -> List[Product]:
        """Get all products by category name (case-insensitive)"""
        return db.query(Product).filter(
            Product.category.ilike(f"%{category_name}%")
        ).all()
    
    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """Create a new product"""
        db_product = Product(
            name=product.name,
            price=product.price,
            description=product.description,
            brand=product.brand,
            stock=product.stock,
            category=product.category,
            picture=product.picture,  # This will be the S3 key if image was uploaded
            rating=0.0,  # Default rating
            ratings=0    # Default ratings count
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    async def create_product_with_image(
        db: Session, 
        product: ProductCreate, 
        image_file: Optional[UploadFile] = None
    ) -> Product:
        """
        Create a new product with optional image upload to S3
        
        Args:
            db: Database session
            product: Product data
            image_file: Optional uploaded image file
            
        Returns:
            Created product with S3 image path if uploaded
        """
        s3_key = None
        
        # Upload image to S3 if provided
        if image_file and image_file.filename:
            logger.info(f"Uploading image for new product: {product.name}")
            s3_key = await s3_service.upload_product_image(image_file, product.name)
            
            if s3_key:
                logger.info(f"Image uploaded successfully: {s3_key}")
                # Update product with S3 key
                product.picture = s3_key
            else:
                logger.warning(f"Failed to upload image for product: {product.name}")
                # Continue without image
                product.picture = None
        
        # Create product (with or without image)
        return ProductService.create_product(db, product)
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Update an existing product"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return None
        
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    async def update_product_with_image(
        db: Session, 
        product_id: int, 
        product_update: ProductUpdate, 
        image_file: Optional[UploadFile] = None,
        delete_current_image: bool = False
    ) -> Optional[Product]:
        """
        Update an existing product with optional image upload to S3
        
        Args:
            db: Database session
            product_id: ID of product to update
            product_update: Product update data
            image_file: Optional new image file to upload
            delete_current_image: Whether to delete current image without replacement
            
        Returns:
            Updated product or None if not found
        """
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            logger.warning(f"Product with ID {product_id} not found")
            return None
        
        # Handle image operations
        old_s3_key = db_product.picture
        new_s3_key = None
        
        # If deleting current image without replacement
        if delete_current_image:
            if old_s3_key:
                logger.info(f"Deleting current image: {old_s3_key}")
                s3_service.delete_product_image(old_s3_key)
            product_update.picture = None
        
        # If uploading new image
        elif image_file and image_file.filename:
            logger.info(f"Uploading new image for product {product_id}: {db_product.name}")
            new_s3_key = await s3_service.upload_product_image(image_file, db_product.name)
            
            if new_s3_key:
                logger.info(f"New image uploaded successfully: {new_s3_key}")
                
                # Delete old image if it exists
                if old_s3_key and old_s3_key != new_s3_key:
                    logger.info(f"Deleting old image: {old_s3_key}")
                    s3_service.delete_product_image(old_s3_key)
                
                # Update product with new S3 key
                product_update.picture = new_s3_key
            else:
                logger.warning(f"Failed to upload new image for product {product_id}")
                # Don't update picture field if upload failed
                if hasattr(product_update, 'picture'):
                    delattr(product_update, 'picture')
        
        # Update product with all changes (including image if successful)
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"Product {product_id} updated successfully")
        return db_product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Delete a product by ID and clean up associated S3 image"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return False
        
        # Delete associated S3 image if it exists
        if db_product.picture:
            logger.info(f"Deleting S3 image for product {product_id}: {db_product.picture}")
            s3_service.delete_product_image(db_product.picture)
        
        db.delete(db_product)
        db.commit()
        logger.info(f"Product {product_id} deleted successfully")
        return True
    
    @staticmethod
    def get_product_image_url(product: Product) -> Optional[str]:
        """
        Get public URL for product image from S3
        
        Args:
            product: Product object
            
        Returns:
            Public image URL or None if no image
        """
        if not product.picture:
            return None
        
        return s3_service.get_image_url(product.picture)

