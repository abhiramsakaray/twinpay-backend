from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.models import User, Transaction
from schemas.schemas import TransactionCreate, TransactionResponse
from utils.database import get_db
from utils.security import verify_password
from utils.helpers import generate_transaction_number
from routers.users import get_current_user

router = APIRouter(tags=["Transactions"])

@router.post("/deposit", status_code=status.HTTP_200_OK)
def deposit(
    transaction: TransactionCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Deposit Money Endpoint"""
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid deposit amount")
    
    current_user.balance += transaction.amount
    
    new_transaction = Transaction(
        user_id=current_user.id,
        transaction_number=generate_transaction_number(current_user.id),
        transaction_type='deposit',
        amount=transaction.amount,
        timestamp=datetime.utcnow()
    )
    
    db.add(new_transaction)
    db.commit()
    
    return {
        "message": "Deposit successful",
        "transaction_number": new_transaction.transaction_number,
        "timestamp": new_transaction.timestamp.isoformat(),
        "new_balance": current_user.balance
    }

@router.post("/withdraw", status_code=status.HTTP_200_OK)
def withdraw(
    transaction: TransactionCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Withdraw Money Endpoint"""
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid withdrawal amount")
    
    if current_user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    if not transaction.pin:
        raise HTTPException(status_code=400, detail="PIN is required for withdrawal")
    
    if not verify_password(transaction.pin, current_user.pin):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    current_user.balance -= transaction.amount
    
    new_transaction = Transaction(
        user_id=current_user.id,
        transaction_number=generate_transaction_number(current_user.id),
        transaction_type='withdraw',
        amount=transaction.amount,
        timestamp=datetime.utcnow()
    )
    
    db.add(new_transaction)
    db.commit()
    
    return {
        "message": "Withdrawal successful",
        "transaction_number": new_transaction.transaction_number,
        "timestamp": new_transaction.timestamp.isoformat(),
        "new_balance": current_user.balance
    }

@router.post("/transfer", status_code=status.HTTP_200_OK)
def transfer(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer Money to Another User Endpoint"""
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid transfer amount")
    
    if current_user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    if not transaction.recipient_twinpay_id:
        raise HTTPException(status_code=400, detail="Recipient TwinPay ID required")
    
    if not transaction.pin:
        raise HTTPException(status_code=400, detail="PIN is required for transfer")
    
    if not verify_password(transaction.pin, current_user.pin):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    recipient = db.query(User).filter(User.twinpay_id == transaction.recipient_twinpay_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer to yourself")
    
    current_user.balance -= transaction.amount
    recipient.balance += transaction.amount
    
    sender_transaction = Transaction(
        user_id=current_user.id,
        transaction_number=generate_transaction_number(current_user.id),
        transaction_type="transfer_out",
        amount=transaction.amount,
        timestamp=datetime.utcnow()
    )
    
    receiver_transaction = Transaction(
        user_id=recipient.id,
        transaction_number=generate_transaction_number(recipient.id),
        transaction_type="transfer_in",
        amount=transaction.amount,
        timestamp=sender_transaction.timestamp
    )
    
    db.add(sender_transaction)
    db.add(receiver_transaction)
    db.commit()
    
    return {
        "message": "Transfer successful",
        "transaction_number": sender_transaction.transaction_number,
        "timestamp": sender_transaction.timestamp.isoformat(),
        "new_balance": current_user.balance,
        "recipient_twinpay_id": recipient.twinpay_id
    }

@router.get("/transactions", response_model=List[TransactionResponse])
def get_all_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get All Transactions for Current User"""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.timestamp.desc()).all()
    
    result = []
    for tx in transactions:
        tx_data = {
            "transaction_number": tx.transaction_number,
            "transaction_type": tx.transaction_type,
            "amount": tx.amount,
            "timestamp": tx.timestamp,
            "recipient_twinpay_id": None
        }
        
        if tx.transaction_type == "transfer_out":
            # Find the recipient by matching transfer_in with same amount and timestamp
            receiver_tx = db.query(Transaction).filter(
                Transaction.transaction_type == "transfer_in",
                Transaction.amount == tx.amount,
                Transaction.timestamp == tx.timestamp
            ).first()
            if receiver_tx:
                recipient = db.query(User).filter(User.id == receiver_tx.user_id).first()
                tx_data["recipient_twinpay_id"] = recipient.twinpay_id
        
        elif tx.transaction_type == "transfer_in":
            # Find the sender by matching transfer_out with same amount and timestamp
            sender_tx = db.query(Transaction).filter(
                Transaction.transaction_type == "transfer_out",
                Transaction.amount == tx.amount,
                Transaction.timestamp == tx.timestamp
            ).first()
            if sender_tx:
                sender = db.query(User).filter(User.id == sender_tx.user_id).first()
                tx_data["recipient_twinpay_id"] = sender.twinpay_id  # Repurposed as sender ID
        
        result.append(tx_data)
    
    return result