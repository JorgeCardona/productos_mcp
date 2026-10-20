# Productos API WEB MCP 📦

Microservicio de gestión de productos híbrido construido con **FastAPI** y **FastMCP** (Model Context Protocol). Proporciona tanto una **API REST** estandarizada con rutas RESTful como un servidor **MCP** con transporte HTTP para asistentes de IA y consumo programático desde entornos como JupyterLab.

---

## 🚀 Características Principales

* **Arquitectura Híbrida**: Sirve endpoints REST (`/docs`) y un servidor MCP (`/mcp`) en el mismo puerto y aplicación FastAPI.
* **Validación Estricta y Seguridad**:
* Modelos **Pydantic** con `strict=True` para prevenir coerciones indeseadas de datos.
* Validación dinámica de tipos en tiempo de ejecución con `@typechecked` (`typeguard`).
* Validación de campos mediante `Field`, incluyendo longitudes máximas, precios no negativos y restricciones de identificadores.
* Manejo de errores para productos inexistentes y datos inválidos.


* **Herramientas Disponibles**:
* Consulta: `list_products`, `get_product`.
* Gestión: `create_product`, `update_product`, `delete_product`.



---

## 📡 Endpoints del Servidor

* **Documentación Swagger / REST**: [https://productos-mcp.onrender.com/docs](https://productos-mcp.onrender.com/docs)
* **Servidor MCP**: [https://productos-mcp.onrender.com/mcp](https://productos-mcp.onrender.com/mcp)

---

## 🛠️ Herramientas MCP / Endpoints REST

| Herramienta / Operación | Método REST | Ruta REST | Descripción | Parámetros principales |
| --- | --- | --- | --- | --- |
| `list_products` | `GET` | `/products` | Lista productos y permite filtrar por categoría y precio máximo | `category: str`, `max_price: float` |
| `get_product` | `GET` | `/products/{product_id}` | Obtiene un producto por su ID (ej. ID 7 o 13) | `product_id: int` |
| `create_product` | `POST` | `/products` | Crea un producto y asigna un ID automáticamente | `name: str`, `price: float`, `category: str`, `description: str` (opcional) |
| `update_product` | `PATCH` | `/products/{product_id}` | Actualiza los campos proporcionados de un producto existente | `product_id: int`, campos opcionales (`name`, `price`, `category`, `description`) |
| `delete_product` | `DELETE` | `/products/{product_id}` | Elimina un producto existente por su ID (ej. ID 13) | `product_id: int` |

---

## 💻 Consumo desde JupyterLab (Python)

### 1. Listar Herramientas (Tools) Disponibles

```python
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession

MCP_URL = "https://productos-mcp.onrender.com/mcp"

async def listar_tools():
    async with streamable_http_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            response = await session.list_tools()

            print("Herramientas disponibles:")

            for tool in response.tools:
                print(f"Nombre: {tool.name}")
                print(f"Descripción: {tool.description}")
                print(f"Argumentos: {tool.input_schema}")
                print("-" * 50)

# Ejecutar en JupyterLab
await listar_tools()

```

---

### 2. Consumo del Servidor MCP (`mcp` + `asyncio`)

El siguiente ejemplo consulta un producto por ID (como el producto 7) y después lista todos los productos disponibles.

```python
import json
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession

MCP_URL = "https://productos-mcp.onrender.com/mcp"

async def consumir_mcp_productos():
    async with streamable_http_client(MCP_URL) as (read, write):

        async with ClientSession(read, write) as session:
            # Inicializar sesión MCP
            await session.initialize()

            # -------------------------------------------------
            # 1. OBTENER UN PRODUCTO POR ID (Ej: ID 7)
            # -------------------------------------------------
            print("CONSULTAR PRODUCTO")

            result = await session.call_tool(
                "get_product",
                arguments={"product_id": 7},
            )

            if result.is_error:
                print("Error MCP:", result.content)
            else:
                for item in result.content:
                    if item.type == "text":
                        try:
                            data = json.loads(item.text)
                            print(json.dumps(
                                data,
                                indent=2,
                                ensure_ascii=False,
                            ))
                        except json.JSONDecodeError:
                            print(item.text)

            print("\n" + "=" * 50)

            # -------------------------------------------------
            # 2. LISTAR TODOS LOS PRODUCTOS
            # -------------------------------------------------
            print("LISTAR PRODUCTOS")

            result = await session.call_tool(
                "list_products",
                arguments={},
            )

            if result.is_error:
                print("Error MCP:", result.content)
            else:
                for item in result.content:
                    if item.type == "text":
                        try:
                            data = json.loads(item.text)
                            print(json.dumps(
                                data,
                                indent=2,
                                ensure_ascii=False,
                            ))
                        except json.JSONDecodeError:
                            print(item.text)

# Ejecutar en JupyterLab
await consumir_mcp_productos()

```

### 3. Crear un producto mediante MCP

```python
import json
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession

MCP_URL = "https://productos-mcp.onrender.com/mcp"

async def crear_producto_mcp():
    async with streamable_http_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "create_product",
                arguments={
                    "name": "Gaming Headset",
                    "price": 89.99,
                    "category": "Electronics",
                    "description": "Wireless gaming headset with noise cancellation",
                },
            )

            if result.is_error:
                print("Error MCP:", result.content)
            else:
                for item in result.content:
                    if item.type == "text":
                        try:
                            data = json.loads(item.text)
                            print("Producto creado:")
                            print(json.dumps(
                                data,
                                indent=2,
                                ensure_ascii=False,
                            ))
                        except json.JSONDecodeError:
                            print(item.text)

# Ejecutar en JupyterLab
await crear_producto_mcp()

```

### 4. Crear un producto mediante la API REST (Ruta estandarizada `POST /products`)

```python
import httpx

response = httpx.post(
    "https://productos-mcp.onrender.com/products",
    json={
        "name": "AI Assistant Subscription – Professional",
        "price": 24.99,
        "category": "Subscription",
        "description": "Monthly AI assistant subscription with advanced models, document analysis, and priority access"
    },
)

print("Estado:", response.status_code)
print("Resultado:", response.json())

```

### 5. Consultar un producto mediante la API REST (Ruta RESTful `GET /products/{product_id}`)

Ejemplo consultando el producto **13**:

```python
import requests

BASE_URL = "https://productos-mcp.onrender.com"

# Consultar endpoint REST /products/{product_id}
response = requests.get(f"{BASE_URL}/products/13")

print("Status Code:", response.status_code)
print("Respuesta REST:", response.json())

```

---

## 🔎 Ejemplos de Filtrado REST

### Filtrar por categoría

```python
import json
import requests

BASE_URL = "https://productos-mcp.onrender.com"

response = requests.get(
    f"{BASE_URL}/products",
    params={"category": "Electronics"},
)

print("🛍️ CATÁLOGO DE PRODUCTOS")
print("=" * 50)
print(f"📡 Estado HTTP: {response.status_code}")
print("📂 Categoría: Electronics")
print("=" * 50)

if response.ok:
    productos = response.json()

    if productos:
        for producto in productos:
            print(f"\n📦 Producto #{producto['id']}")
            print(f"    🏷️ Nombre:       {producto['name']}")
            print(f"    💰 Precio:       ${producto['price']:,.2f}")
            print(f"    📂 Categoría:    {producto['category']}")
            print(f"    📝 Descripción:  {producto.get('description') or 'Sin descripción'}")
            print("-" * 50)

        print(f"\n✅ Total de productos encontrados: {len(productos)}")
    else:
        print("⚠️ No se encontraron productos en esta categoría.")
else:
    print("❌ Error al consultar la API:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

```

### Filtrar por precio máximo

```python
import requests

BASE_URL = "https://productos-mcp.onrender.com"

response = requests.get(
    f"{BASE_URL}/products",
    params={"max_price": 100.0},
)

print("🛍️ CATÁLOGO DE PRODUCTOS")
print("=" * 55)
print(f"📡 Estado HTTP: {response.status_code}")
print("💰 Filtro: Precio máximo de $100.00")
print("=" * 55)

if response.ok:
    productos = response.json()

    if productos:
        for producto in productos:
            print(f"\n📦 Producto #{producto['id']}")
            print(f"    🏷️ Nombre:      {producto['name']}")
            print(f"    💵 Precio:      ${producto['price']:,.2f}")
            print(f"    📂 Categoría:    {producto['category']}")
            print(
                f"    📝 Descripción: "
                f"{producto.get('description') or 'Sin descripción'}"
            )
            print("-" * 55)

        print(f"\n✅ Total de productos encontrados: {len(productos)}")
    else:
        print("\n⚠️ No se encontraron productos por debajo del precio indicado.")
else:
    print("\n❌ Error al consultar la API:")
    try:
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print(response.text)

```

---

## ⚠️ Consideraciones

* **Almacenamiento en memoria**: Los productos creados, actualizados o eliminados se mantienen únicamente durante la vida del proceso del servidor. Un reinicio puede restaurar el catálogo inicial (el cual incluye elementos clave como el producto **7** y el producto **13**).
* **Identificadores automáticos**: El ID de un producto nuevo se asigna automáticamente. Utiliza el ID devuelto por la operación de creación para consultarlo o actualizarlo.
* **Validación estricta**: Los modelos Pydantic aplican restricciones de tipos y campos. Las solicitudes que no cumplan el esquema pueden devolver `422 Unprocessable Entity`.
* **Errores REST**: Los productos inexistentes generan `404 Not Found`; los errores de la lógica de negocio generan `400 Bad Request`.
* **Actualización parcial**: `PATCH /products/{product_id}` recibe el identificador en la ruta y los campos opcionales que se desean modificar.
* **Despliegue**: El servicio utiliza la variable de entorno `PORT` y puede ejecutarse en plataformas como Render.

---

## 🧰 Tecnologías Utilizadas

* **FastAPI**: API REST y documentación OpenAPI.
* **FastMCP**: Registro y exposición de herramientas MCP.
* **Pydantic**: Validación de datos.
* **Typeguard**: Comprobación de tipos durante la ejecución.
* **Uvicorn**: Servidor ASGI.
* **Requests / HTTPX**: Consumo de endpoints REST.
* **MCP Python SDK**: Conexión al servidor MCP desde Python y JupyterLab.

---

## 📌 Resumen

**Productos API WEB MCP** permite listar, consultar, crear, actualizar y eliminar productos mediante dos interfaces alineadas con los mejores estándares: una API RESTful limpia y un servidor MCP. Ambas comparten la lógica de negocio y el almacenamiento en memoria, permitiendo integrar el catálogo con aplicaciones web, programas Python y asistentes de inteligencia artificial.
