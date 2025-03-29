from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv

from models.models import User
from schemas.schemas import UserCreate, UserLogin, Token
from utils.database import get_db
from utils.security import get_password_hash, verify_password, create_access_token
from utils.helpers import generate_twinpay_id

# Load environment variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

router = APIRouter(tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """User Registration Endpoint"""
    try:
        existing_user = db.query(User).filter(User.mobile_number == user.mobile_number).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Mobile number already registered")
        
        if user.email and db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if user.aadhar_number and db.query(User).filter(User.aadhar_number == user.aadhar_number).first():
            raise HTTPException(status_code=400, detail="Aadhar number already registered")
        
        if user.pan_card and db.query(User).filter(User.pan_card == user.pan_card).first():
            raise HTTPException(status_code=400, detail="PAN card already registered")
        
        twinpay_id = generate_twinpay_id(user.full_name, user.email, db)
        
        new_user = User(
            mobile_number=user.mobile_number,
            full_name=user.full_name,
            twinpay_id=twinpay_id,
            hashed_password=get_password_hash(user.password),
            pin=get_password_hash(user.pin),
            balance=0.0,
            aadhar_number=user.aadhar_number,
            pan_card=user.pan_card,
            date_of_birth=user.date_of_birth,
            email=user.email,
            address=user.address
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "User registered successfully", "twinpay_id": twinpay_id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed due to duplicate data")

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """User Login Endpoint"""
    user = db.query(User).filter(User.mobile_number == user_login.mobile_number).first()
    
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mobile_number}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# OAuth2 compatible login
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = db.query(User).filter(User.mobile_number == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mobile_number}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}