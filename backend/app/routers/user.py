from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import datetime, timedelta

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    oauth2_scheme,
    verify_token
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token
)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    if User.select().where(User.username == user_data.username).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if User.select().where(User.email == user_data.email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_data.password)
    user = User.create(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    return user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = User.get(User.username == form_data.username)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    user.last_login = datetime.now()
    user.save()

    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token)
    username: str = payload.get("sub")
    try:
        user = User.get(User.username == username)
        return user
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    if user_update.username and user_update.username != current_user.username:
        if User.select().where(User.username == user_update.username).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.email and user_update.email != current_user.email:
        if User.select().where(User.email == user_update.email).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    if user_update.profile_picture is not None:
        current_user.profile_picture = user_update.profile_picture

    if user_update.latitude is not None and user_update.longitude is not None:
        current_user.latitude = user_update.latitude
        current_user.longitude = user_update.longitude
        current_user.last_location_update = datetime.now()

    current_user.save()
    return current_user

@router.post("/me/location")
async def update_location(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
):
    current_user.latitude = latitude
    current_user.longitude = longitude
    current_user.last_location_update = datetime.now()
    current_user.save()
    return {"message": "Location updated successfully"}
