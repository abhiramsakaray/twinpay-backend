import random
import string
from datetime import datetime
from typing import Optional
from fastapi import HTTPException

def generate_twinpay_id(full_name: str, email: Optional[str], db) -> str:
    """Generate TwinPay ID from full name or email if full name-based ID exists"""
    from models.models import User
    
    base_id = full_name.lower().replace(' ', '')
    twinpay_id = f"{base_id}@twinpay"
    
    # Check if TwinPay ID already exists
    if db.query(User).filter(User.twinpay_id == twinpay_id).first():
        if not email:
            raise HTTPException(status_code=400, detail="Email required when TwinPay ID based on full name is taken")
        # Use email (without domain) as TwinPay ID
        email_base = email.split('@')[0].lower().replace('.', '')
        twinpay_id = f"{email_base}@twinpay"
        if db.query(User).filter(User.twinpay_id == twinpay_id).first():
            raise HTTPException(status_code=400, detail="TwinPay ID based on email is also taken")
    
    return twinpay_id

def generate_transaction_number(user_id: int) -> str:
    """Generate a unique transaction number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{timestamp}{random_suffix}{user_id:04d}"