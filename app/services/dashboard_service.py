from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository


class DashboardService:
    """
    Orquesta datos de Productos y Ordenes para armar las metricas
    del panel administrativo. No hace consultas SQL directamente:
    se apoya en los repositorios de cada dominio.
    """

    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)
        self.order_repository = OrderRepository(db)

    def get_stats(self) -> dict:
        return {
            "monthly_sales": self.order_repository.get_monthly_sales_total(),
            "pending_orders": self.order_repository.count_pending_orders(),
            "low_stock_count": self.product_repository.count_low_stock(),
            "inventory_value": self.product_repository.get_inventory_value(),
        }