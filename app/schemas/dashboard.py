from pydantic import BaseModel


class DashboardStats(BaseModel):
    monthly_sales: float
    pending_orders: int
    low_stock_count: int
    inventory_value: float