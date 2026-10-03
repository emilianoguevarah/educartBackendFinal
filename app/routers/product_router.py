from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductFilterParams
from ..services.product_service import ProductCreate, ProductService
from ..core.security import get_current_user, get_current_admin_user 


product_router = APIRouter(prefix="/products", tags=["Products"]) 


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Retorna una instancia del servicio de productos con la sesión de BD inyectada."""
    return ProductService(db)


# READ (Alertas de Stock) - RESTRINGIDO A ADMIN
@product_router.get(
    "/alerts",
    response_model=List[ProductResponse],
    dependencies=[Depends(get_current_admin_user)],
)
def get_stock_alerts(service: ProductService = Depends(get_product_service)):
    """Devuelve solo los productos en estado Alerta o Agotado, para el dashboard."""
    return service.get_low_stock_products()

# READ (Listar todos) - ACCESO PÚBLICO (Visitante y Cliente)
@product_router.get("/", response_model=List[ProductResponse])
def list_products(
    categories: Optional[List[str]] = Query(None, description="Lista de categorías"),
    price_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    price_max: Optional[float] = Query(None, description="Precio máximo"),
    search: Optional[str] = Query(None, description="Texto a buscar en el nombre del producto"),
    service: ProductService = Depends(get_product_service),
    sort_by: Optional[str] = Query(None, description="Campo: 'price', 'created_at', 'name'"),
    order: Optional[str] = Query("asc", description="Dirección: 'asc' o 'desc'"),
):
    """Permite a Visitantes y Clientes explorar el catálogo y usar filtros."""
    filters = ProductFilterParams(
        categories=categories,
        price_min=price_min,
        price_max=price_max,
        search=search,
        sort_by=sort_by,
        order=order
    )
    return service.get_filtered_products(filters)


#  READ (Por ID) - ACCESO PÚBLICO (Visitante y Cliente)
@product_router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    """Permite a Visitantes ver el detalle del producto."""
    product = service.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado."
        )
    return product

# CREATE - RESTRINGIDO A ADMIN
@product_router.post(
    "/", 
    response_model=ProductResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)] # <-- SOLO ADMIN
)
def create_product(
    product_data: ProductCreate, 
    service: ProductService = Depends(get_product_service)
):
    """Crea un nuevo producto (Gestión de Inventario)."""
    return service.create_product(product_data)

# UPDATE - RESTRINGIDO A ADMIN
@product_router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def update_product_partial(
    product_id: int, 
    product_data: ProductUpdate, 
    service: ProductService = Depends(get_product_service)
    
):
    """Actualiza parcialmente uno o más campos de un producto existente."""
    product = service.update_product(product_id, product_data)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado para actualizar."
        )
    return product

#  DELETE - RESTRINGIDO A ADMIN
@product_router.delete(
    "/{product_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)]
)
def delete_product(
    product_id: int, 
    service: ProductService = Depends(get_product_service)
):
    """Elimina un producto (Gestión de Inventario)."""
    success = service.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado para eliminar."
        )
    return