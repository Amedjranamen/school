from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..auth import get_current_user, require_role
from ..models import User, UserCreate, UserUpdate, UserInDB
from ..database import users_collection
from passlib.context import CryptContext
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=List[UserInDB])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get all users with pagination and filtering (Admin/Librarian only)"""
    
    # Build filter query
    filter_query = {}
    
    if role:
        filter_query["role"] = role
    
    if search:
        filter_query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"username": {"$regex": search, "$options": "i"}}
        ]
    
    # Get users with pagination
    cursor = users_collection.find(filter_query).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    # Convert to UserInDB format
    result = []
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["password_hash"]  # Never return password hash
        result.append(UserInDB(**user))
    
    return result

@router.get("/stats")
async def get_users_stats(
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get user statistics"""
    
    # Count users by role
    pipeline = [
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]
    
    role_counts = {}
    async for doc in users_collection.aggregate(pipeline):
        role_counts[doc["_id"]] = doc["count"]
    
    # Total users
    total_users = await users_collection.count_documents({})
    
    # Active users (assuming we have an 'active' field)
    active_users = await users_collection.count_documents({"active": True})
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "users_by_role": role_counts
    }

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get user by ID (Admin/Librarian only)"""
    
    user = await users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["id"] = str(user["_id"])
    del user["_id"]
    del user["password_hash"]  # Never return password hash
    
    return UserInDB(**user)

@router.post("/", response_model=UserInDB)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role(["admin"]))
):
    """Create new user (Admin only)"""
    
    # Check if email or username already exists
    existing_user = await users_collection.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )
    
    # Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create user document
    user_doc = {
        "id": str(uuid.uuid4()),
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hashed_password,
        "role": user_data.role,
        "full_name": user_data.full_name,
        "class": user_data.class_name,
        "phone": user_data.phone,
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert user
    result = await users_collection.insert_one(user_doc)
    
    # Return created user
    user_doc["id"] = user_doc["id"]
    del user_doc["_id"]
    del user_doc["password_hash"]
    
    return UserInDB(**user_doc)

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_role(["admin"]))
):
    """Update user (Admin only)"""
    
    # Check if user exists
    existing_user = await users_collection.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build update document
    update_doc = {"updated_at": datetime.utcnow()}
    
    if user_data.username is not None:
        # Check if new username is already taken
        username_check = await users_collection.find_one({
            "username": user_data.username,
            "id": {"$ne": user_id}
        })
        if username_check:
            raise HTTPException(status_code=400, detail="Username already taken")
        update_doc["username"] = user_data.username
    
    if user_data.email is not None:
        # Check if new email is already taken
        email_check = await users_collection.find_one({
            "email": user_data.email,
            "id": {"$ne": user_id}
        })
        if email_check:
            raise HTTPException(status_code=400, detail="Email already taken")
        update_doc["email"] = user_data.email
    
    if user_data.password is not None:
        update_doc["password_hash"] = pwd_context.hash(user_data.password)
    
    if user_data.role is not None:
        update_doc["role"] = user_data.role
    
    if user_data.full_name is not None:
        update_doc["full_name"] = user_data.full_name
    
    if user_data.class_name is not None:
        update_doc["class"] = user_data.class_name
    
    if user_data.phone is not None:
        update_doc["phone"] = user_data.phone
    
    if user_data.active is not None:
        update_doc["active"] = user_data.active
    
    # Update user
    await users_collection.update_one(
        {"id": user_id},
        {"$set": update_doc}
    )
    
    # Return updated user
    updated_user = await users_collection.find_one({"id": user_id})
    updated_user["id"] = str(updated_user["_id"])
    del updated_user["_id"]
    del updated_user["password_hash"]
    
    return UserInDB(**updated_user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role(["admin"]))
):
    """Delete user (Admin only)"""
    
    # Check if user exists
    existing_user = await users_collection.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has active loans (prevent deletion)
    from .loans import loans_collection
    active_loans = await loans_collection.count_documents({
        "user_id": user_id,
        "status": {"$in": ["borrowed", "overdue"]}
    })
    
    if active_loans > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete user with active loans"
        )
    
    # Delete user
    await users_collection.delete_one({"id": user_id})
    
    return {"message": "User deleted successfully"}

@router.post("/bulk-import")
async def bulk_import_users(
    users_data: List[UserCreate],
    current_user: User = Depends(require_role(["admin"]))
):
    """Bulk import users from CSV data (Admin only)"""
    
    results = {
        "created": 0,
        "errors": [],
        "duplicates": 0
    }
    
    for i, user_data in enumerate(users_data):
        try:
            # Check if user already exists
            existing_user = await users_collection.find_one({
                "$or": [
                    {"email": user_data.email},
                    {"username": user_data.username}
                ]
            })
            
            if existing_user:
                results["duplicates"] += 1
                results["errors"].append({
                    "row": i + 1,
                    "error": f"User {user_data.username} already exists"
                })
                continue
            
            # Hash password
            hashed_password = pwd_context.hash(user_data.password)
            
            # Create user document
            user_doc = {
                "id": str(uuid.uuid4()),
                "username": user_data.username,
                "email": user_data.email,
                "password_hash": hashed_password,
                "role": user_data.role,
                "full_name": user_data.full_name,
                "class": user_data.class_name,
                "phone": user_data.phone,
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert user
            await users_collection.insert_one(user_doc)
            results["created"] += 1
            
        except Exception as e:
            results["errors"].append({
                "row": i + 1,
                "error": str(e)
            })
    
    return results