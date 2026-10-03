from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardStats

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_admin_user)],
)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@dashboard_router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(service: DashboardService = Depends(get_dashboard_service)):
    """Devuelve las metricas clave para el panel administrativo."""
    return service.get_stats()