"""Product and Variant Database Services"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.models.product import Product, ProductVariant
from backend.schemas.product import ProductCreate, ProductSearchQuery
from backend.core.logging import logger


class ProductService:
    @staticmethod
    def get_product(db: Session, product_id: str) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def search_products(db: Session, query_params: ProductSearchQuery) -> List[Product]:
        term = f"%{query_params.query.strip().lower()}%"
        q = db.query(Product).filter(
            or_(
                Product.title.ilike(term),
                Product.brand.ilike(term),
                Product.model_number.ilike(term)
            )
        )
        if query_params.category:
            q = q.filter(Product.category == query_params.category)
        return q.order_by(desc(Product.total_reviews)).limit(query_params.limit).all()

    @staticmethod
    def list_products(db: Session, category: Optional[str] = "laptops", limit: int = 50) -> List[Product]:
        q = db.query(Product)
        if category:
            q = q.filter(Product.category == category)
        return q.order_by(desc(Product.total_reviews)).limit(limit).all()

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        product = Product(
            title=product_in.title,
            brand=product_in.brand,
            category=product_in.category,
            model_number=product_in.model_number,
            image_url=product_in.image_url,
            specifications=product_in.specifications
        )
        db.add(product)
        db.flush()

        if product_in.variants:
            for v_in in product_in.variants:
                variant = ProductVariant(
                    product_id=product.id,
                    variant_sku=v_in.variant_sku,
                    cpu=v_in.cpu,
                    ram=v_in.ram,
                    storage=v_in.storage,
                    gpu=v_in.gpu,
                    display_spec=v_in.display_spec,
                    raw_variant_string=v_in.raw_variant_string
                )
                db.add(variant)
        
        db.commit()
        db.refresh(product)
        return product
