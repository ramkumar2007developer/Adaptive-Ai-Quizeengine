from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.schemas.user_schemas import CreateUserRequest, UserResponse
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
async def register_user(request: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    """Create a new user profile."""
    repo = UserRepository(db)
    
    # Check if username exists
    existing = await repo.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
        
    user = await repo.create(
        username=request.username,
        email=request.email,
        display_name=request.display_name
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at
    )
