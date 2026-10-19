Aquí tienes la documentación completa y actualizada de Productos API WEB MCP, conservando la misma estructura del README de la calculadora y corrigiendo los atributos del SDK de MCP para tu entorno: `tool.input_schema` y `result.is_error`.

Writing

# Productos API WEB MCP 📦

Microservicio de gestión de productos híbrido construido con **FastAPI** y **FastMCP** (Model Context Protocol). Proporciona tanto una **API REST** para integración web estándar como un servidor **MCP** con transporte HTTP para asistentes de IA y consumo programático desde entornos como JupyterLab.

---

## 🚀 Características Principales

- **Arquitectura Híbrida**: Sirve endpoints REST (`/docs`) y un servidor MCP (`/mcp`) en el mismo puerto y aplicación FastAPI.
- **Validación Estricta y Seguridad**:
  - Modelos **Pydantic** con `strict=True` para prevenir coerciones indeseadas de datos.
  - Validación dinámica de tipos en tiempo de ejecución con `@typechecked` (`typeguard`).
  - Validación de campos mediante `Field`, incluyendo longitudes máximas, precios no negativos y restricciones de identificadores.
  - Manejo de errores para productos inexistentes y datos inválidos.
- **Herramientas Disponibles**:
  - Consulta: `list_products`, `get_product`.
  - Gestión: `create_product`, `update_product`, `delete_product`.

---

## 📡 Endpoints del Servidor

- **Documentación Swagger / REST**: https://productos-mcp.onrender.com/docs
- **Servidor MCP**: https://productos-mcp.onrender.com/mcp

---

## 🛠️ Herramientas MCP / Endpoints REST

| Herramienta | Tipo | Descripción | Parámetros |
| --- | --- | --- | --- |
| `list_products` | Consulta | Lista productos y permite filtrar por categoría y precio máximo | `category: str`, `max_price: float` |
| `get_product` | Consulta | Obtiene un producto por su ID | `product_id: int` |
| `create_product` | Gestión | Crea un producto y asigna un ID automáticamente | `name: str`, `price: float`, `category: str`, `description: str` opcional |
| `update_product` | Gestión | Actualiza los campos proporcionados de un producto existente | `product_id: int`, `name: str`, `price: float`, `category: str`, `description: str` opcionales |
| `delete_product` | Gestión | Elimina un producto existente por su ID | `product_id: int` |

---

## 💻 Consumo desde JupyterLab (Python)

### 1\. LISTAR TOOLS

```
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

### 2\. Consumo del Servidor MCP (`mcp` \+ `nest_asyncio`)

El siguiente ejemplo consulta un producto por ID y después lista todos los productos disponibles.

```
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
            # 1. OBTENER UN PRODUCTO POR ID
            # -------------------------------------------------
            print("CONSULTAR PRODUCTO")

            result = await session.call_tool(
                "get_product",
                arguments={"product_id": 1},
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

### 3\. Crear un producto mediante MCP

```
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

### 4\. Crear un producto mediante la API REST
```
import httpx

response = httpx.post(
    "https://productos-mcp.onrender.com/products/create_product",
    json={
        "name": "Gaming Headset",
        "price": 89.99,
        "category": "Electronics",
        "description": "Wireless gaming headset with noise cancellation"
    },
)

print("Estado:", response.status_code)
print("Resultado:", response.json())
```

### 5\. Consultar un producto mediante la API REST
```
import requests

BASE_URL = "https://productos-mcp.onrender.com"

# Probar endpoint REST /products/get_product
response = requests.get(
    f"{BASE_URL}/products/get_product",
    params={"product_id": 13},
)

print("Status Code:", response.status_code)
print("Respuesta REST:", response.json())
```

---

## 🔎 Ejemplos de Filtrado REST

### Filtrar por categoría

```
import requests

BASE_URL = "https://productos-mcp.onrender.com"

response = requests.get(
    f"{BASE_URL}/products/list_products",
    params={"category": "Electronics"},
)

print("Status Code:", response.status_code)
print("Respuesta REST:", response.json())
```

### Filtrar por precio máximo

```
import requests

BASE_URL = "https://productos-mcp.onrender.com"

response = requests.get(
    f"{BASE_URL}/products/list_products",
    params={"max_price": 100.0},
)

print("Status Code:", response.status_code)
print("Respuesta REST:", response.json())
```

---

## ⚠️ Consideraciones

- **Almacenamiento en memoria**: Los productos creados, actualizados o eliminados se mantienen únicamente durante la vida del proceso del servidor. Un reinicio puede restaurar el catálogo inicial.
- **Identificadores automáticos**: El ID de un producto nuevo se asigna automáticamente. Utiliza el ID devuelto por la operación de creación para consultarlo o actualizarlo.
- **Validación estricta**: Los modelos Pydantic aplican restricciones de tipos y campos. Las solicitudes que no cumplan el esquema pueden devolver `422 Unprocessable Entity`.
- **Errores REST**: Los productos inexistentes generan `404 Not Found`; los errores de la lógica de negocio generan `400 Bad Request`.
- **Actualización parcial**: `PATCH /products/update_product` recibe el `product_id` y los campos que se desean actualizar.
- **Despliegue**: El servicio utiliza la variable de entorno `PORT` y puede ejecutarse en plataformas como Render.

---

## 🧰 Tecnologías Utilizadas

- **FastAPI**: API REST y documentación OpenAPI.
- **FastMCP**: Registro y exposición de herramientas MCP.
- **Pydantic**: Validación de datos.
- **Typeguard**: Comprobación de tipos durante la ejecución.
- **Uvicorn**: Servidor ASGI.
- **Requests / HTTPX**: Consumo de endpoints REST.
- **MCP Python SDK**: Conexión al servidor MCP desde Python y JupyterLab.

---

## 📌 Resumen

**Productos API WEB MCP** permite listar, consultar, crear, actualizar y eliminar productos mediante dos interfaces: REST y MCP. Ambas comparten la lógica de negocio y el almacenamiento en memoria, permitiendo integrar el catálogo con aplicaciones web, programas Python y asistentes de inteligencia artificial.

Correcciones importantes incluidas:

- `tool.input_schema` para mostrar los argumentos de las herramientas.
- `result.is_error` para comprobar errores al invocar herramientas MCP.
- Ejemplos independientes para listar herramientas, consumir MCP, crear productos y utilizar REST.

Los endpoints y nombres corresponden al código `main.py` que compartiste.
