from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import asc, desc
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate
from sqlalchemy import func

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_id_for_update(self, product_id: int) -> Optional[Product]:
        """
        Bloquea la fila para evitar condiciones de carrera durante la compra.
        """
        return self.db.query(Product).filter(Product.id == product_id).with_for_update().first()

    def list_low_stock(self) -> List[Product]:
        """
        Devuelve los productos en estado Alerta o Agotado
        (stock_current <= stock_min). Usado para el dashboard de alertas.
        """
        return self.db.query(Product).filter(Product.stock_current <= Product.stock_min).all()

    def count_low_stock(self) -> int:
        return self.db.query(Product).filter(Product.stock_current <= Product.stock_min).count()

    def get_inventory_value(self) -> float:
        """
        Calcula el valor total del inventario (precio * stock) directamente
        en la base de datos, en vez de traer todo a Python y sumar ahí.
        """"""el coalesce es solo para que devuelva 0.0 en vez de None si no hay productos todavía"""
        total = self.db.query(func.coalesce(func.sum(Product.price * Product.stock_current), 0.0)).scalar()
        return float(total)
    def list_filtered(
        self, 
        category: Optional[str] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None, 
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc"
    ) -> List[Product]:
        """
        Aplica filtros dinámicos a la consulta de productos.
        """
        query = self.db.query(Product)

        if category:
            query = query.join(Category).filter(Category.name == category)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        
        if search:
      
            query = query.filter(Product.name.ilike(f"%{search}%"))
        
        if sort_by:
            sort_column = None
            
         
            if sort_by == "price":
                sort_column = Product.price
            elif sort_by == "name":
                sort_column = Product.name
            elif sort_by == "created_at":
                sort_column = Product.created_at
            
            if sort_column:
                if order == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))

        return query.all()

    def create(self, product_in: ProductCreate) -> Product:
        # Usamos model_dump()
        db_product = Product(**product_in.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, product_id: int, product_in: ProductUpdate) -> Optional[Product]:
        db_product = self.get_by_id(product_id)
        if not db_product:
            return None

        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, product_id: int) -> bool:
        db_product = self.get_by_id(product_id)
        if not db_product:
            return False
        self.db.delete(db_product)
        self.db.commit()
        return True