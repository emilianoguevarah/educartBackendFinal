from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from .routers import order_router, product_router, category_router, cart_item_router, health_router, auth_router, cart_router,  dashboard_router
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(cart_router)
app.include_router(cart_item_router)
app.include_router(order_router)
app.include_router(dashboard_router)



@app.get("/")
def root():
    return {"message": "Bienvenido a la API del E-Commerce 🚀"}



