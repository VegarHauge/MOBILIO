from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.deps import get_db
from services.product_service import ProductService
from models.schemas import ProductResponse, ProductCreate, ProductUpdate
from models.user import User
from utils.auth_utils import get_admin_user
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = ProductService.get_all_products(db)
    return products

@router.get("/brand/{brand_name}", response_model=List[ProductResponse])
def get_products_by_brand(brand_name: str, db: Session = Depends(get_db)):
    """Get all products by brand"""
    products = ProductService.get_products_by_brand(db, brand_name)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No products found for brand: {brand_name}"
        )
    return products

@router.get("/category/{category_name}", response_model=List[ProductResponse])
def get_products_by_category(category_name: str, db: Session = Depends(get_db)):
    """Get all products by category"""
    products = ProductService.get_products_by_category(db, category_name)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No products found for category: {category_name}"
        )
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID"""
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    stock: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new product (Admin only)"""
    product_data = ProductCreate(
        name=name,
        price=price,
        description=description,
        brand=brand,
        category=category,
        stock=stock
    )
    return await ProductService.create_product_with_image(db, product_data, image)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    stock: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update an existing product (Admin only)"""
    # Build update dict only with provided fields
    update_dict = {}
    if name is not None:
        update_dict['name'] = name
    if price is not None:
        update_dict['price'] = price
    if description is not None:
        update_dict['description'] = description
    if brand is not None:
        update_dict['brand'] = brand
    if category is not None:
        update_dict['category'] = category
    if stock is not None:
        update_dict['stock'] = stock
    
    product_update = ProductUpdate(**update_dict)
    updated_product = await ProductService.update_product_with_image(db, product_id, product_update, image)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return updated_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a product (Admin only)"""
    success = ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return None