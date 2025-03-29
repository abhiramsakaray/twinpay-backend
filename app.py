import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import auth, users, transactions
from utils.database import create_tables

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="TwinPay Digital Wallet",
    description="API for TwinPay Digital Wallet services",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    # Add production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api/users")
app.include_router(transactions.router, prefix="/api/transactions")

# Initialize database tables
@app.on_event("startup")
def startup_event():
    create_tables()
    print("Database tables initialized successfully!")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to TwinPay Digital Wallet API"}

# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)