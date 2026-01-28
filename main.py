from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from fastmcp import FastMCP

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
    Product(id=1, name="Laptop", price=999.99, category="Electronics", description="High performance laptop"),
    Product(id=2, name="Mouse", price=29.99, category="Electronics", description="Wireless mouse"),
    Product(id=3, name="Desk Chair", price=299.99, category="Furniture", description="Ergonomic chair")
]
next_id = 4

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    mcp.run(transport="http", host="0.0.0.0", port=port)
