
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db 
from ..schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService 
from app.core.security import get_current_admin_user

category_router = APIRouter(prefix="/categories", tags=["Categories"])

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    """Retorna una instancia del servicio de categorías con la sesión de BD inyectada."""
    return CategoryService(db)

# READ (Listar todos) - PUBLICO
@category_router.get("/", response_model=List[CategoryResponse])
def list_categories(service: CategoryService = Depends(get_category_service)):
    """Obtiene una lista de todas las categorías."""
    return service.get_all_categories()

# READ (Por ID) - PUBLICO
@category_router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    """Obtiene una categoría específica por su ID."""
    category = service.get_category_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada."
        )
    return category

# CREATE - RESTRINGIDO A ADMIN
@category_router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
)
def create_category(
    category_data: CategoryCreate, 
    service: CategoryService = Depends(get_category_service)
):
    """Crea una nueva categoría."""
    return service.create_category(category_data)

# UPDATE - RESTRINGIDO A ADMIN
@category_router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def update_category(
    category_id: int, 
    category_data: CategoryUpdate, 
    service: CategoryService = Depends(get_category_service)
):
    """Actualiza una categoría existente."""
    category = service.update_category(category_id, category_data)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada para actualizar."
        )
    return category

# DELETE - RESTRINGIDO A ADMIN
@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
)
def delete_category(
    category_id: int, 
    service: CategoryService = Depends(get_category_service)
):
    """Elimina una categoría por su ID."""
    success = service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada para eliminar."
        )
    return