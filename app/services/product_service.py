from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilterParams
from app.models.product import Product

class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def get_filtered_products(self, filters: ProductFilterParams) -> List[Product]:
        """
        Llama al repositorio aplicando los filtros recibidos del router.
        """
        return self.repository.list_filtered(
            category=filters.categories[0] if filters.categories else None,
            min_price=filters.price_min,
            max_price=filters.price_max,
            search=filters.search,
            sort_by=filters.sort_by,
            order=filters.order,
        )

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.repository.get_by_id(product_id)

    def create_product(self, product_data: ProductCreate) -> Product:
        return self.repository.create(product_data)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        return self.repository.update(product_id, product_data)

    def delete_product(self, product_id: int) -> bool:
        return self.repository.delete(product_id)
    
    def get_low_stock_products(self):
        return self.repository.list_low_stock()