from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from utils.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    twinpay_id = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    pin = Column(String, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    aadhar_number = Column(String, unique=True, nullable=True)
    pan_card = Column(String, unique=True, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    email = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    transaction_number = Column(String(40), unique=True, nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)