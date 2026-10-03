# app/repositories/order_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import exc
from typing import Optional, List
from sqlalchemy import func, extract
from datetime import datetime

from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderCreate # Solo para tipado

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Recupera una orden por su ID."""
        return self.db.query(Order).get(order_id)

    def get_monthly_sales_total(self) -> float:
        """
        Suma el total_amount de las ordenes del mes en curso.
        Igual que en ProductRepository, la suma la hace la base de datos.
        """
        now = datetime.utcnow()
        total = (
            self.db.query(func.coalesce(func.sum(Order.total_amount), 0.0))
            .filter(extract('year', Order.order_date) == now.year)
            .filter(extract('month', Order.order_date) == now.month)
            .scalar()
        )
        return float(total)

    def count_pending_orders(self) -> int:
        return self.db.query(Order).filter(Order.status == "Pending").count()
    
    def create_order_transaction(
        self, 
        user_id: int, 
        order_data: OrderCreate, 
        items_to_add: List[dict],
        final_total: float
    ) -> Order:
        """
        CREA LA ORDEN DENTRO DE UNA TRANSACCIÓN. 
        Nota: La lógica de STOCK DEBE ESTAR EN EL SERVICE, no aquí.
        Este método asume que el stock ya fue actualizado en el Service.
        """
        
        # 1. Crear la cabecera de la Orden
        new_order = Order(
            user_id=user_id,
            shipping_address=order_data.shipping_address,
            total_amount=final_total,
            locality=order_data.locality,
        )
        self.db.add(new_order)
        self.db.flush() # Importante para obtener el ID de la nueva orden antes del commit
        
        order_items = [
            OrderItem(
                order_id=new_order.id, 
                product_id=item['product_id'], 
                quantity=item['quantity'], 
                unit_price=item['price']
            )
            for item in items_to_add
        ]
        self.db.add_all(order_items)
        
       
        
        return new_order
    
    
    
    def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        """Busca la orden y actualiza su estado."""
        order = self.db.query(Order).get(order_id)
        if order:
            order.status = new_status
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
        return order