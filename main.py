from fastapi import FastAPI, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

# Initialize FastAPI app
app = FastAPI(
    title="First UV Pro API",
    description="A comprehensive FastAPI application with multiple endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# Data Models (Pydantic Schemas)
# ============================================

class User(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ramesh Kumar Sah",
                "email": "ramesh@example.com",
                "age": 25
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)

class Item(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    quantity: int = Field(default=1, ge=0)
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample Product",
                "description": "This is a sample product",
                "price": 99.99,
                "quantity": 10
            }
        }

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)

# ============================================
# In-Memory Database (for demonstration)
# ============================================

users_db: Dict[str, User] = {}
items_db: Dict[str, Item] = {}

# ============================================
# Root & Health Check Endpoints
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Hello from first-uv-pro! - from Ramesh Kumar Sah",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users_count": len(users_db),
        "items_count": len(items_db)
    }

# ============================================
# User Management Endpoints
# ============================================

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: User):
    """Create a new user"""
    user.id = str(uuid4())
    user.created_at = datetime.now()
    users_db[user.id] = user
    return user

@app.get("/users", response_model=List[User], tags=["Users"])
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return")
):
    """Get all users with pagination"""
    users_list = list(users_db.values())
    return users_list[skip:skip + limit]

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: str = Path(..., description="The ID of the user to retrieve")):
    """Get a specific user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return users_db[user_id]

@app.put("/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(
    user_id: str = Path(..., description="The ID of the user to update"),
    user_update: UserUpdate = Body(...)
):
    """Update a user's information"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    stored_user = users_db[user_id]
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(stored_user, field, value)
    
    users_db[user_id] = stored_user
    return stored_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(user_id: str = Path(..., description="The ID of the user to delete")):
    """Delete a user"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    del users_db[user_id]
    return None

@app.get("/users/search/by-email", response_model=List[User], tags=["Users"])
async def search_users_by_email(email: str = Query(..., description="Email to search for")):
    """Search users by email"""
    matching_users = [user for user in users_db.values() if email.lower() in user.email.lower()]
    return matching_users

# ============================================
# Item/Product Management Endpoints
# ============================================

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: Item):
    """Create a new item"""
    item.id = str(uuid4())
    item.created_at = datetime.now()
    items_db[item.id] = item
    return item

@app.get("/items", response_model=List[Item], tags=["Items"])
async def get_all_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter")
):
    """Get all items with pagination and optional price filtering"""
    items_list = list(items_db.values())
    
    # Apply price filters if provided
    if min_price is not None:
        items_list = [item for item in items_list if item.price >= min_price]
    if max_price is not None:
        items_list = [item for item in items_list if item.price <= max_price]
    
    return items_list[skip:skip + limit]

@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: str = Path(..., description="The ID of the item to retrieve")):
    """Get a specific item by ID"""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return items_db[item_id]

@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(
    item_id: str = Path(..., description="The ID of the item to update"),
    item_update: ItemUpdate = Body(...)
):
    """Update an item's information"""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    stored_item = items_db[item_id]
    update_data = item_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(stored_item, field, value)
    
    items_db[item_id] = stored_item
    return stored_item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: str = Path(..., description="The ID of the item to delete")):
    """Delete an item"""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    del items_db[item_id]
    return None

# ============================================
# Statistics & Analytics Endpoints
# ============================================

@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get overall statistics"""
    total_users = len(users_db)
    total_items = len(items_db)
    
    total_inventory_value = sum(item.price * item.quantity for item in items_db.values())
    avg_item_price = sum(item.price for item in items_db.values()) / total_items if total_items > 0 else 0
    
    return {
        "users": {
            "total": total_users
        },
        "items": {
            "total": total_items,
            "total_inventory_value": round(total_inventory_value, 2),
            "average_price": round(avg_item_price, 2)
        },
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# Utility Endpoints
# ============================================

@app.post("/reset", tags=["Utility"])
async def reset_database():
    """Reset all data (clear the in-memory database)"""
    users_db.clear()
    items_db.clear()
    return {
        "message": "Database reset successfully",
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# Main Entry Point
# ============================================

def main():
    """Run the FastAPI application"""
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
