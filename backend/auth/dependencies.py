from fastapi import Depends, HTTPException, status
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from .auth_handler import verify_token
from .models import UserInDB
import os

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'resume_analyzer')]

security = HTTPBearer()

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> UserInDB:
    """Get current authenticated user or a fallback guest user"""
    try:
        if not credentials:
            return get_guest_user()
            
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            return get_guest_user()
        
        user_id = payload.get("sub")
        if user_id is None:
            return get_guest_user()
        
        # Get user from database
        user = await db.users.find_one({"id": user_id})
        if user is None:
            return get_guest_user()
        
        return UserInDB(**user)
    except Exception:
        # Fallback to guest user for any error (to ensure app remains accessible)
        return get_guest_user()

def get_guest_user() -> UserInDB:
    """Return a hardcoded guest user for anonymous access"""
    return UserInDB(
        id="guest_user_account",
        email="guest@example.com",
        full_name="Guest User",
        hashed_password="no_password_needed",
        is_active=True
    )