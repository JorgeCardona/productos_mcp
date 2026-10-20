# main.py
# API REST + MCP
# REST: https://productos-mcp.onrender.com/docs
# MCP:  https://productos-mcp.onrender.com/mcp

import logging
import math
import os
from contextlib import asynccontextmanager
from functools import wraps
from typing import Optional, TypedDict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from typeguard import typechecked
from fastmcp import FastMCP
from mcp.types import ToolAnnotations


# =========================================================
# CONFIGURACIÓN
# =========================================================

VERSION = "2.1.3"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("productos")


# =========================================================
# LOGGING: REST Y MCP
# =========================================================

def registrar_llamada(origen: str, nombre: str):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(
                "[%s] INICIO | herramienta=%s",
                origen,
                nombre,
            )
            try:
                resultado = func(*args, **kwargs)
                logger.info(
                    "[%s] ÉXITO | herramienta=%s",
                    origen,
                    nombre,
                )
                return resultado
            except Exception:
                logger.exception(
                    "[%s] ERROR | herramienta=%s",
                    origen,
                    nombre,
                )
                raise

        return wrapper

    return decorador


# =========================================================
# MODELOS Y TYPEDICTS
# =========================================================

class Product(BaseModel):
    model_config = ConfigDict(strict=True)

    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0, allow_inf_nan=False)
    category: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)


class ProductCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0, allow_inf_nan=False)
    category: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)


class ProductUpdate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    price: Optional[float] = Field(
        default=None,
        ge=0,
        allow_inf_nan=False,
    )
    category: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: Optional[str] = Field(default=None, max_length=2000)


class DeleteResult(TypedDict):
    message: str
    product_id: int
    name: str


# =========================================================
# BASE DE DATOS EN MEMORIA
# =========================================================

products_db: dict[int, Product] = {
    1: Product(
        id=1, name="Laptop Pro 16", price=1999.99,
        category="Electronics",
        description="High performance laptop for developers",
    ),
    2: Product(
        id=2, name="Wireless Mouse", price=39.99,
        category="Electronics",
        description="Ergonomic wireless mouse",
    ),
    3: Product(
        id=3, name="Ergonomic Desk Chair", price=349.99,
        category="Furniture",
        description="Comfortable chair for long work sessions",
    ),
    4: Product(
        id=4, name="Mechanical Keyboard", price=129.99,
        category="Electronics",
        description="Mechanical keyboard with RGB lighting",
    ),
    5: Product(
        id=5, name="27'' 4K Monitor", price=499.99,
        category="Electronics",
        description="Ultra HD monitor for productivity",
    ),
    6: Product(
        id=6, name="Streaming Subscription – Premium",
        price=15.99, category="Subscription",
        description="Access to movies and TV shows in 4K with multiple profiles",
    ),
    7: Product(
        id=7, name="LLM Subscription – Enterprise",
        price=299.99, category="Subscription",
        description="Enterprise-grade LLM subscription with SLA",
    ),
    8: Product(
        id=8, name="Cloud Storage 1TB", price=9.99,
        category="Cloud",
        description="1TB cloud storage billed monthly",
    ),
    9: Product(
        id=9, name="Cloud Compute Credits", price=199.99,
        category="Cloud",
        description="Monthly cloud compute credits",
    ),
    10: Product(
        id=10, name="API Access Plan", price=99.99,
        category="Software",
        description="Premium API access with higher rate limits",
    ),
    11: Product(
        id=11, name="Cybersecurity Monitoring", price=149.99,
        category="Service",
        description="24/7 cybersecurity monitoring service",
    ),
    12: Product(
        id=12, name="Data Analytics Dashboard", price=79.99,
        category="Software",
        description="Advanced analytics and reporting dashboard",
    ),
    13: Product(
        id=13, name="AI Model Fine-Tuning Service", price=499.99,
        category="Service",
        description="Custom fine-tuning service for AI models",
    ),
}

next_id = max(products_db.keys(), default=0) + 1


# =========================================================
# LÓGICA DE NEGOCIO COMPARTIDA
# =========================================================

@typechecked
def listar_productos(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
) -> list[Product]:
    if max_price is not None:
        if not math.isfinite(max_price) or max_price < 0:
            raise ValueError("max_price debe ser un número finito >= 0.")

    resultados = list(products_db.values())

    if category:
        resultados = [
            p for p in resultados
            if p.category.casefold() == category.casefold()
        ]

    if max_price is not None:
        resultados = [
            p for p in resultados
            if p.price <= max_price
        ]

    return resultados


@typechecked
def obtener_producto(product_id: int) -> Product:
    producto = products_db.get(product_id)

    if producto is None:
        raise LookupError(f"No existe el producto con ID {product_id}.")

    return producto


@typechecked
def crear_producto(
    name: str,
    price: float,
    category: str,
    description: Optional[str] = None,
) -> Product:
    global next_id

    name = name.strip()
    category = category.strip()

    if not name:
        raise ValueError("El nombre no puede estar vacío.")

    if not category:
        raise ValueError("La categoría no puede estar vacía.")

    if not math.isfinite(price) or price < 0:
        raise ValueError("El precio debe ser finito y no negativo.")

    producto = Product(
        id=next_id,
        name=name,
        price=price,
        category=category,
        description=description,
    )

    products_db[next_id] = producto
    next_id += 1

    return producto


@typechecked
def actualizar_producto(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> Product:
    producto_actual = obtener_producto(product_id)

    # Validar y preparar los nuevos valores antes de mutar nada
    nuevo_nombre = producto_actual.name
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("El nombre no puede estar vacío.")
        nuevo_nombre = name

    nuevo_precio = producto_actual.price
    if price is not None:
        if not math.isfinite(price) or price < 0:
            raise ValueError("El precio debe ser finito y no negativo.")
        nuevo_precio = price

    nueva_categoria = producto_actual.category
    if category is not None:
        category = category.strip()
        if not category:
            raise ValueError("La categoría no puede estar vacía.")
        nueva_categoria = category

    nueva_descripcion = producto_actual.description if description is None else description

    # Actualización atómica segura usando model_copy para evitar corrupción parcial
    producto_actualizado = producto_actual.model_copy(
        update={
            "name": nuevo_nombre,
            "price": nuevo_precio,
            "category": nueva_categoria,
            "description": nueva_descripcion,
        }
    )

    products_db[product_id] = producto_actualizado
    return producto_actualizado


@typechecked
def eliminar_producto(product_id: int) -> DeleteResult:
    producto = products_db.pop(product_id, None)

    if producto is None:
        raise LookupError(f"No existe el producto con ID {product_id}.")

    return {
        "message": "Producto eliminado correctamente.",
        "product_id": product_id,
        "name": producto.name,
    }


# =========================================================
# SERVIDOR MCP Y HERRAMIENTAS NATIVAS
# =========================================================

mcp = FastMCP("Productos")


def anotaciones(
    titulo: str,
    *,
    solo_lectura: bool,
    idempotente: bool,
) -> ToolAnnotations:
    return ToolAnnotations(
        title=titulo,
        readOnlyHint=solo_lectura,
        destructiveHint=False,
        idempotentHint=idempotente,
        openWorldHint=False,
    )


@mcp.tool(
    name="list_products",
    description="Lista los productos. Permite filtrar por categoría y precio máximo.",
    annotations=anotaciones("List products", solo_lectura=True, idempotente=True),
    meta={"service": "productos", "version": VERSION, "category": "catalogo", "tool": "list_products"}
)
@typechecked
@registrar_llamada("MCP", "list_products")
def tool_list_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
) -> list[dict]:
    return [
        producto.model_dump()
        for producto in listar_productos(category, max_price)
    ]


@mcp.tool(
    name="get_product",
    description="Obtiene un producto por su ID.",
    annotations=anotaciones("Get product", solo_lectura=True, idempotente=True),
    meta={"service": "productos", "version": VERSION, "category": "catalogo", "tool": "get_product"}
)
@typechecked
@registrar_llamada("MCP", "get_product")
def tool_get_product(product_id: int) -> dict:
    return obtener_producto(product_id).model_dump()


@mcp.tool(
    name="create_product",
    description="Crea un producto y asigna un ID automáticamente.",
    annotations=anotaciones("Create product", solo_lectura=False, idempotente=False),
    meta={"service": "productos", "version": VERSION, "category": "catalogo", "tool": "create_product"}
)
@typechecked
@registrar_llamada("MCP", "create_product")
def tool_create_product(
    name: str,
    price: float,
    category: str,
    description: Optional[str] = None,
) -> dict:
    return crear_producto(
        name, price, category, description
    ).model_dump()


@mcp.tool(
    name="update_product",
    description="Actualiza los campos proporcionados de un producto existente.",
    annotations=anotaciones("Update product", solo_lectura=False, idempotente=True),
    meta={"service": "productos", "version": VERSION, "category": "catalogo", "tool": "update_product"}
)
@typechecked
@registrar_llamada("MCP", "update_product")
def tool_update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    return actualizar_producto(
        product_id, name, price, category, description
    ).model_dump()


@mcp.tool(
    name="delete_product",
    description="Elimina un producto existente por su ID.",
    annotations=anotaciones("Delete product", solo_lectura=False, idempotente=True),
    meta={"service": "productos", "version": VERSION, "category": "catalogo", "tool": "delete_product"}
)
@typechecked
@registrar_llamada("MCP", "delete_product")
def tool_delete_product(product_id: int) -> DeleteResult:
    return eliminar_producto(product_id)


# =========================================================
# FASTAPI + CICLO DE VIDA MCP
# =========================================================

mcp_app = mcp.http_app(path="/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(app):
        yield


app = FastAPI(
    title="Productos API",
    description="Microservicio de productos con API REST y MCP",
    version=VERSION,
    lifespan=lifespan,
)


# =========================================================
# ENDPOINTS REST (ESTÁNDARES REST)
# =========================================================

def ejecutar_rest(func, *args):
    try:
        return func(*args)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, OverflowError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/products",
    response_model=list[Product],
    operation_id="rest_list_products",
    tags=["Products"],
)
@registrar_llamada("REST", "list_products")
def rest_list_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
):
    return ejecutar_rest(listar_productos, category, max_price)


@app.get(
    "/products/{product_id}",
    response_model=Product,
    operation_id="rest_get_product",
    tags=["Products"],
)
@registrar_llamada("REST", "get_product")
def rest_get_product(product_id: int):
    return ejecutar_rest(obtener_producto, product_id)


@app.post(
    "/products",
    response_model=Product,
    operation_id="rest_create_product",
    tags=["Products"],
    status_code=201,
)
@registrar_llamada("REST", "create_product")
def rest_create_product(product: ProductCreate):
    return ejecutar_rest(
        crear_producto,
        product.name,
        product.price,
        product.category,
        product.description,
    )


@app.patch(
    "/products/{product_id}",
    response_model=Product,
    operation_id="rest_update_product",
    tags=["Products"],
)
@registrar_llamada("REST", "update_product")
def rest_update_product(product_id: int, update: ProductUpdate):
    return ejecutar_rest(
        actualizar_producto,
        product_id,
        update.name,
        update.price,
        update.category,
        update.description,
    )


@app.delete(
    "/products/{product_id}",
    response_model=DeleteResult,
    operation_id="rest_delete_product",
    tags=["Products"],
)
@registrar_llamada("REST", "delete_product")
def rest_delete_product(product_id: int):
    return ejecutar_rest(eliminar_producto, product_id)


@app.get("/", tags=["Info"])
def root():
    return {
        "name": "Productos API + MCP",
        "version": VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "mcp": "/mcp",
        "tools": [
            "list_products",
            "get_product",
            "create_product",
            "update_product",
            "delete_product",
        ],
        "storage": "in-memory",
    }


# =========================================================
# MONTAR MCP EN FASTAPI
# =========================================================

app.mount("/mcp", mcp_app)


# =========================================================
# ARRANQUE LOCAL / RENDER
# =========================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )
