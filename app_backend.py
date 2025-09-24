from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from faker import Faker
import random
from datetime import datetime, timedelta
app = FastAPI(title = "Living Ledger Backend")

#Generate SMS Data
fake = Faker()
banks = ["HDFCBK", "SBIINB", "ICICIBK"]
merchants = ["Amazon", "Flipkart", "Swiggy", "Netflix", "Salary", "Paytm","zomato", "uber", "ola", "irctc", "makemytrip", "redbus", "electricity", "gas", "water", "mobile recharge", "dth","atm", "withdrawal", "deposit", "balance", "transfer","emi", "loan", "credit card", "bill payment","spotify", "hotstar", "sonyliv", "bookmyshow", "gaming", "steam"]
types = ["debit", "credit"]


# Define categories and associated keywords
CATEGORIES = {
    "Food": ["zomato", "swiggy", "dominos", "pizza", "mcdonald", "kfc"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "snapdeal"],
    "Travel": ["uber", "ola", "irctc", "makemytrip", "redbus"],
    "Utilities": ["electricity", "gas", "water", "mobile recharge", "dth"],
    "Banking": ["atm", "withdrawal", "deposit", "balance", "transfer"],
    "Bills": ["emi", "loan", "credit card", "bill payment"],
    "Entertainment": ["netflix", "spotify", "hotstar", "sonyliv", "bookmyshow", "gaming", "steam"]
}

#Function to categorize transactions
def categorize_transaction(merchant, txn_type):
    merchant_lower = merchant.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in merchant_lower:
                return category
    if txn_type.lower() in ["deposit", "withdrawal", "transfer"]:
        return "Banking"
    return "Other"

#Function to generate data
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
        
        txn = {
            "bank": bank,
            "type": txn_type,
            "amount": amount,
            "merchant": merchant,
            "date": txn_date.strftime("%Y-%m-%d"),
            "balance": balance
        }
        txn["category"] = categorize_transaction(merchant, txn_type)
        data.append(txn)
    return data


@app.get("/mock-sms")
def get_mock_sms():
    mock_sms = generate_sms_data()
    return JSONResponse(content={"transactions": mock_sms})


#Health Check
@app.get("/")
def read_root():
    return {"message": "Living Ledger Backend is running!"}



