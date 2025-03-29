from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from models.models import User
from schemas.schemas import UserResponse, PasswordUpdate, PinUpdate
from utils.database import get_db
from utils.security import oauth2_scheme, verify_password, get_password_hash, jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(tags=["Users"])

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobile_number: str = payload.get("sub")
        if mobile_number is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.mobile_number == mobile_number).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/profile", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile information"""
    return current_user

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change User Password Endpoint"""
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect current password")
    
    current_user.hashed_password = get_password_hash(password_update.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/change-pin", status_code=status.HTTP_200_OK)
def change_pin(
    pin_update: PinUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change User PIN Endpoint"""
    if not verify_password(pin_update.current_pin, current_user.pin):
        raise HTTPException(status_code=401, detail="Incorrect current PIN")
    
    current_user.pin = get_password_hash(pin_update.new_pin)
    db.commit()
    
    return {"message": "PIN updated successfully"}

@router.get("/balance")
def check_balance(
    pin: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check User Balance Endpoint"""
    if not pin:
        raise HTTPException(status_code=400, detail="PIN is required to check balance")
    
    if not verify_password(pin, current_user.pin):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    return {"balance": current_user.balance}