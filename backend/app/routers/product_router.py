from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.product_schema import ProductResponse, ProductBase, ProductUpdate
from app.services.product_service import get_products, get_product, update_product, delete_product
from app.models.product import Product
from app.cache.cache_service import CacheService
from app.cache.cache_keys import CacheKeys
from app.routers.auth_router import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    cache_key = CacheKeys.PRODUCTS_CATALOG
    
    cached_products = CacheService.get_cache(cache_key)
    if cached_products:
        return cached_products
        
    products = get_products(db, skip=skip, limit=limit)
    serialized = [ProductResponse.from_orm(p).dict() for p in products]
    CacheService.set_cache(cache_key, serialized, ttl=300)
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = CacheKeys.get_product_key(product_id)
    
    cached_product = CacheService.get_cache(cache_key)
    if cached_product:
        return cached_product
        
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    serialized = ProductResponse.from_orm(db_product).dict()
    CacheService.set_cache(cache_key, serialized, ttl=300)
    
    return db_product

@router.post("/", response_model=ProductResponse)
def create_product(product: ProductBase, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    CacheService.invalidate_cache(CacheKeys.PRODUCTS_CATALOG)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
@router.patch("/{product_id}", response_model=ProductResponse)
def modify_product(product_id: int, product_update: ProductUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_product = update_product(db, product_id, product_update.dict(exclude_unset=True))
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    CacheService.invalidate_cache(CacheKeys.PRODUCTS_CATALOG)
    CacheService.invalidate_cache(CacheKeys.get_product_key(product_id))
    return updated_product

@router.delete("/{product_id}", status_code=204)
def remove_product(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
        
    CacheService.invalidate_cache(CacheKeys.PRODUCTS_CATALOG)
    CacheService.invalidate_cache(CacheKeys.get_product_key(product_id))
    return None
