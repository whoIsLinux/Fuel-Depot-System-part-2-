from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import User
from schemas import UserLogin, Token, UserResponse
from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.username == user_login.username).first()
    
    if not user:
        # First time login - create new user
        # Determine role based on username or set default
        role = "Manager" if "manager" in user_login.username.lower() else "Attendant"
        
        hashed_password = get_password_hash(user_login.password)
        user = User(
            username=user_login.username,
            hashed_password=hashed_password,
            role=role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Existing user - verify password
        if not verify_password(user_login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # In a real app, you'd add token to blacklist here
    return {"message": "Successfully logged out"}