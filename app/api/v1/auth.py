"""
Authentication endpoints.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import (authenticate_user, create_access_token,
                           get_current_active_user, get_password_hash)
from app.models.auth import Token, User, UserCreate
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, users_db

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    """
    Register a new user.

    Args:
        user: User registration data

    Returns:
        Created user object
    """
    # Check username
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    user_dict["is_active"] = True
    user_dict["id"] = len(users_db) + 1  # Simple auto-incrementing ID

    users_db[user.username] = user_dict
    return User(**user_dict)


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
