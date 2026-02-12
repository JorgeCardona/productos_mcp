from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from fastmcp import FastMCP
from mcp.types import Tool

app = FastAPI(title="Productos API", version="1.0.0")

# ---------------------------
# Models
# ---------------------------
class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    category: str
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    product_id: int
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None

# ---------------------------
# In-Memory Database
# ---------------------------
products_db = [
    Product(id=1, name="Laptop Pro 16", price=1999.99, category="Electronics", description="High performance laptop for developers"),
    Product(id=2, name="Wireless Mouse", price=39.99, category="Electronics", description="Ergonomic wireless mouse"),
    Product(id=3, name="Ergonomic Desk Chair", price=349.99, category="Furniture", description="Comfortable chair for long work sessions"),
    Product(id=4, name="Mechanical Keyboard", price=129.99, category="Electronics", description="Mechanical keyboard with RGB lighting"),
    Product(id=5, name="27'' 4K Monitor", price=499.99, category="Electronics", description="Ultra HD monitor for productivity"),
    Product(id=6, name="Streaming Subscription – Premium", price=15.99, category="Subscription", description="Access to movies and TV shows in 4K with multiple profiles"),
    Product(id=7, name="LLM Subscription – Enterprise", price=299.99, category="Subscription", description="Enterprise-grade LLM subscription with SLA"),
    Product(id=8, name="Cloud Storage 1TB", price=9.99, category="Cloud", description="1TB cloud storage billed monthly"),
    Product(id=9, name="Cloud Compute Credits", price=199.99, category="Cloud", description="Monthly cloud compute credits"),
    Product(id=10, name="API Access Plan", price=99.99, category="Software", description="Premium API access with higher rate limits"),
    Product(id=11, name="Cybersecurity Monitoring", price=149.99, category="Service", description="24/7 cybersecurity monitoring service"),
    Product(id=12, name="Data Analytics Dashboard", price=79.99, category="Software", description="Advanced analytics and reporting dashboard"),
    Product(id=13, name="AI Model Fine-Tuning Service", price=499.99, category="Service", description="Custom fine-tuning service for AI models")
]

next_id = 14

# ---------------------------
# Endpoints
# ---------------------------

@app.get("/products/list_products", response_model=List[Product])
async def list_products(category: Optional[str] = None, max_price: Optional[float] = None):
    """List all products with optional filtering."""
    results = products_db
    if category:
        results = [p for p in results if p.category.lower() == category.lower()]
    if max_price:
        results = [p for p in results if p.price <= max_price]
    return results

@app.get("/products/get_product", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID."""
    for p in products_db:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products/create_product", response_model=Product)
async def create_product(name: str, price: float, category: str, description: Optional[str] = None):
    """Create a new product."""
    global next_id
    new_product = Product(id=next_id, name=name, price=price, category=category, description=description)
    products_db.append(new_product)
    next_id += 1
    return new_product

@app.post("/products/update_product", response_model=Product)
async def update_product(product_id: int, name: Optional[str] = None, price: Optional[float] = None, category: Optional[str] = None, description: Optional[str] = None):
    """Update an existing product."""
    for p in products_db:
        if p.id == product_id:
            if name is not None: p.name = name
            if price is not None: p.price = price
            if category is not None: p.category = category
            if description is not None: p.description = description
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/delete_product", response_model=dict)
async def delete_product(product_id: int):
    """Delete a product."""
    global products_db
    for i, p in enumerate(products_db):
        if p.id == product_id:
            del products_db[i]
            return {"message": "Product deleted", "product_id": product_id}
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/")
async def root():
    return {"message": "Productos MCP Server Running"}

# ---------------------------
# MCP Server Wrapper
# ---------------------------

mcp = FastMCP.from_fastapi(app)

# ---------------------------
# Explicit MCP Standard Method
# ---------------------------

@mcp.list_tools()
async def list_tools() -> List[Tool]:
    """
    Standard MCP tools/list method.
    """
    return [
        Tool(
            name="list_products",
            description="List all products with optional filtering by category and max_price",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "max_price": {"type": "number"}
                }
            }
        ),
        Tool(
            name="get_product",
            description="Get a product by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "required": ["product_id"]
            }
        ),
        Tool(
            name="create_product",
            description="Create a new product",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "category": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "price", "category"]
            }
        ),
        Tool(
            name="update_product",
            description="Update an existing product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "category": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["product_id"]
            }
        ),
        Tool(
            name="delete_product",
            description="Delete a product by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "required": ["product_id"]
            }
        )
    ]

# ---------------------------
# Run Server
# ---------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    mcp.run(transport="http", host="0.0.0.0", port=port)
