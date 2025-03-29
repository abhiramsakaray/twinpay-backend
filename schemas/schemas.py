import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict, EmailStr

class UserCreate(BaseModel):
    mobile_number: str
    full_name: str
    password: str
    pin: str
    aadhar_number: Optional[str] = None
    pan_card: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator('mobile_number')
    @classmethod
    def validate_mobile_number(cls, v):
        if not re.match(r'^\+?1?\d{10,14}$', v):
            raise ValueError('Invalid mobile number format')
        return v

    @field_validator('pin')
    @classmethod
    def validate_pin(cls, v):
        if not re.match(r'^\d{4}$', v):
            raise ValueError('PIN must be 4 digits')
        return v

    @field_validator('aadhar_number')
    @classmethod
    def validate_aadhar_number(cls, v):
        if v and not re.match(r'^\d{12}$', v):
            raise ValueError('Aadhar number must be 12 digits')
        return v

    @field_validator('pan_card')
    @classmethod
    def validate_pan_card(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', v):
            raise ValueError('Invalid PAN card format (e.g., ABCDE1234F)')
        return v

class UserLogin(BaseModel):
    mobile_number: str
    password: str

class UserResponse(BaseModel):
    mobile_number: str
    full_name: str
    twinpay_id: str
    balance: float
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TransactionCreate(BaseModel):
    amount: float
    transaction_type: str
    recipient_twinpay_id: Optional[str] = None
    pin: Optional[str] = None

    @field_validator('pin')
    @classmethod
    def validate_pin(cls, v):
        if v and not re.match(r'^\d{4}$', v):
            raise ValueError('PIN must be 4 digits')
        return v

class TransactionResponse(BaseModel):
    transaction_number: str
    transaction_type: str
    amount: float
    timestamp: datetime
    recipient_twinpay_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class PinUpdate(BaseModel):
    current_pin: str
    new_pin: str
    
    @field_validator('new_pin')
    @classmethod
    def validate_pin(cls, v):
        if not re.match(r'^\d{4}$', v):
            raise ValueError('PIN must be 4 digits')
        return v