from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from faker import Faker
import random
from datetime import datetime, timedelta
app = FastAPI(title = "Living Ledger Backend")

fake = Faker()
banks = ["HDFCBK", "SBIINB", "ICICIBK"]
merchants = ["Amazon", "Flipkart", "Swiggy", "Netflix", "Salary", "Paytm"]
types = ["debit", "credit"]

def generate_sms_data(num_entries=50, start_date="2025-07-01"):
    data = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    
    for _ in range(num_entries):
        txn_date = start + timedelta(days=random.randint(0, 90))
        txn_type = random.choice(types)
        merchant = random.choice(merchants)
        amount = random.randint(50, 50000) if txn_type=="debit" else random.randint(100, 100000)
        balance = random.randint(5000, 100000)
        bank = random.choice(banks)
        
        data.append({
            "bank": bank,
            "type": txn_type,
            "amount": amount,
            "merchant": merchant,
            "date": txn_date.strftime("%Y-%m-%d"),
            "balance": balance
        })
    return data

@app.get("/mock-sms")
def get_mock_sms():
    mock_sms = generate_sms_data()
    return JSONResponse(content={"transactions": mock_sms})

#Health Check
@app.get("/")
def read_root():
    return {"message": "Living Ledger Backend is running!"}



