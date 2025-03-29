# TwinPay Digital Wallet API

TwinPay is a **FastAPI-based** digital wallet service providing user authentication, transactions, and balance management.

## 🚀 Features
- User Registration & Login
- JWT Authentication
- User Profile & Balance Management
- Secure Transactions (Deposit, Withdraw, Transfer)
- PostgreSQL Database Integration

---

## 🛠️ Project Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/abhiramsakaray/twinpay-backend.git
cd twinpay-backend
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Edit the `.env` file in the project root:
```ini
DATABASE_URL=postgresql://postgresql_username:postgresql_password@localhost:5432/twinpay_wallet
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
Replace `username`, `password`, and `twinpay_wallet` with your PostgreSQL credentials.

---

## 🗄️ PostgreSQL Setup

### Install PostgreSQL (If not installed)
- **Ubuntu:** `sudo apt update && sudo apt install postgresql postgresql-contrib`
- **Mac:** `brew install postgresql`
- **Windows:** Download and install from [PostgreSQL Official Site](https://www.postgresql.org/download/)

### Create a PostgreSQL Database
```sql
CREATE DATABASE twinpay_wallet;
CREATE USER twinpay_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE twinpay_db TO twinpay_user;
```

### Run Database Migrations
```bash
alembic upgrade head
```

---

## 🚀 Run the Server
```bash
uvicorn app:app --reload
```

Open API Docs:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛠️ API Endpoints

### Authentication
- `POST /api/register` – Register a new user
- `POST /api/login` – Login and get access token
- `POST /api/token` – Get JWT access token

### Users
- `GET /api/users/profile` – Get user profile
- `POST /api/users/change-password` – Change user password
- `POST /api/users/change-pin` – Change transaction PIN
- `GET /api/users/balance` – Check wallet balance

### Transactions
- `POST /api/transactions/deposit` – Deposit money
- `POST /api/transactions/withdraw` – Withdraw money
- `POST /api/transactions/transfer` – Transfer money to another user
- `GET /api/transactions/transactions` – Get transaction history

---

## ✅ Contribution Guide
1. Fork the repo & create a new branch
2. Commit your changes
3. Push and create a PR

---

## 📄 License
MIT License. Feel free to modify and use!

---

## ⚡ Contact
For any issues, reach out at [sakrayabhiram@gmail.com](mailto:sakrayabhiram@gmail.com).

