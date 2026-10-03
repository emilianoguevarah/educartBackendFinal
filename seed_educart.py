"""
Script de carga inicial para EduCart.
Crea el usuario admin (si no existe), las categorias y 12 productos reales
sacados del mockup "pantallas.zip" (los mismos nombres, precios e imagenes
que definio la consigna).

Uso:
    1) Backend corriendo en http://127.0.0.1:8000
    2) Frontend corriendo en http://localhost:5173, con las imagenes copiadas en
       educartFrontFinal/public/products/10.webp ... 21.webp
    3) python seed_educart.py

No necesita librerias externas (solo la libreria estandar de Python).
"""

import json
import urllib.request
import urllib.error

BACKEND_URL = "http://127.0.0.1:8000"
IMAGE_BASE = "http://localhost:5173/products"  # carpeta public/products del frontend

ADMIN_USER = {
    "name": "Toro Admin",
    "username": "toroadmin",
    "email": "toro@test.com",
    "password": "admin1234",
    "role": "admin",
}

CATEGORIES = ["Books", "Stationery", "Tech Gadgets", "Workspace"]

# name, description, price, category, sku, stock_current, stock_min, image_num
PRODUCTS = [
    ("Advanced Mathematics Textbook", "Libro de texto avanzado de matematicas para estudiantes universitarios.", 49.99, "Books", "BOOK-001", 25, 10, 10),
    ("Smart Notebook", "Cuaderno inteligente reutilizable, compatible con apps de notas.", 24.99, "Stationery", "STA-002", 40, 15, 11),
    ("Wireless Earbuds", "Auriculares inalambricos con cancelacion de ruido basica.", 89.99, "Tech Gadgets", "TEC-003", 15, 5, 12),
    ("Ergonomic Study Chair", "Silla ergonomica pensada para largas horas de estudio.", 199.99, "Workspace", "WORK-004", 8, 5, 13),
    ("Programming Fundamentals Book", "Introduccion a la programacion, ideal para primer anio.", 34.99, "Books", "BOOK-005", 30, 10, 14),
    ("Graphing Calculator", "Calculadora cientifica graficadora.", 129.99, "Tech Gadgets", "TEC-006", 3, 5, 15),   # Alerta
    ("Premium Highlighters Set", "Set de resaltadores de alta calidad, 12 colores.", 12.99, "Stationery", "STA-007", 50, 20, 16),
    ("Adjustable Desk Lamp", "Lampara de escritorio con brillo ajustable y USB.", 39.99, "Workspace", "WORK-008", 0, 5, 17),   # Agotado
    ("Scientific Research Methods", "Guia de metodologia de la investigacion cientifica.", 59.99, "Books", "BOOK-009", 12, 10, 18),
    ("Noise Cancelling Headphones", "Auriculares con cancelacion activa de ruido.", 149.99, "Tech Gadgets", "TEC-010", 20, 5, 19),
    ("Premium Notebook Set", "Set de 3 cuadernos tapa dura.", 19.99, "Stationery", "STA-011", 35, 15, 20),
    ("Whiteboard Marker Set", "Set de marcadores para pizarra blanca, 8 colores.", 8.99, "Workspace", "WORK-012", 60, 20, 21),
]


def call(method, path, body=None, token=None):
    url = f"{BACKEND_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    def _safe_json(raw_bytes):
        raw = raw_bytes.decode("utf-8", errors="replace") or "null"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw[:300]}

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, _safe_json(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, _safe_json(e.read())


def main():
    # 1) Registrar admin (ignoramos error si ya existe)
    status, body = call("POST", "/auth/register", ADMIN_USER)
    if status == 201 or status == 200:
        print(f"[OK] Admin creado: {ADMIN_USER['username']}")
    else:
        print(f"[INFO] Registro admin devolvio {status}: {body} (probablemente ya existia, seguimos)")

    # 2) Login
    status, body = call("POST", "/auth/login", {
        "username": ADMIN_USER["username"],
        "password": ADMIN_USER["password"],
    })
    if status != 200:
        print(f"[ERROR] No se pudo loguear como admin: {status} {body}")
        return
    token = body["access_token"]
    print("[OK] Login admin correcto.")

    # 3) Crear categorias
    category_ids = {}
    for name in CATEGORIES:
        status, body = call("POST", "/categories/", {"name": name}, token=token)
        if status in (200, 201):
            category_ids[name] = body["id"]
            print(f"[OK] Categoria creada: {name} (id={body['id']})")
        else:
            # si ya existe, la buscamos en el listado
            _, all_cats = call("GET", "/categories/")
            existing = next((c for c in all_cats if c["name"] == name), None)
            if existing:
                category_ids[name] = existing["id"]
                print(f"[INFO] Categoria ya existia: {name} (id={existing['id']})")
            else:
                print(f"[ERROR] No se pudo crear ni encontrar categoria {name}: {status} {body}")

    # 4) Crear productos (evitamos duplicar si ya existe el SKU)
    _, existing_products = call("GET", "/products/")
    existing_skus = {p["sku"] for p in existing_products} if isinstance(existing_products, list) else set()

    for name, desc, price, cat_name, sku, stock, stock_min, img_num in PRODUCTS:
        if sku in existing_skus:
            print(f"[INFO] Producto ya existia (sku={sku}): {name}")
            continue
        if cat_name not in category_ids:
            print(f"[SKIP] {name}: falta categoria {cat_name}")
            continue
        payload = {
            "name": name,
            "description": desc,
            "price": price,
            "category_id": category_ids[cat_name],
            "sku": sku,
            "stock_current": stock,
            "stock_min": stock_min,
            "image_url": f"{IMAGE_BASE}/{img_num}.webp",
            "rating": 4,
        }
        status, body = call("POST", "/products/", payload, token=token)
        if status in (200, 201):
            print(f"[OK] Producto creado: {name}")
        else:
            print(f"[ERROR] {name}: {status} {body}")

    print("\nListo. Recarga el catalogo en el frontend para verlos.")


if __name__ == "__main__":
    main()
