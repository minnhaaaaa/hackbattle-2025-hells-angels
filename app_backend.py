from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from faker import Faker
from collections import defaultdict
import random
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
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

def detect_fraud(transactions):
    fraud_alerts = []
    category_amounts = defaultdict(list)
    for txn in transactions:
        category_amounts[txn["category"]].append(txn["amount"])
    category_avg = {cat: sum(vals)/len(vals) for cat, vals in category_amounts.items()}
    # Count frequency per day per category
    freq_counter = defaultdict(lambda: defaultdict(int))
    for txn in transactions:
        date = txn["date"]
        cat = txn["category"]
        freq_counter[cat][date] += 1
    # Track merchants used before
    known_merchants = set()
    for txn in transactions:
        merchant = txn["merchant"]
        cat = txn["category"]
        amount = txn["amount"]
        date = txn["date"]
        txn_type = txn["type"]
        alerts = []
        # High-value outlier
        avg = category_avg.get(cat, 0)
        if txn_type.lower() == "debit" and amount > 3 * avg:
            alerts.append("High-value transaction anomaly")
        # Unusual frequency (more than 5 txns in a day per category)
        if freq_counter[cat][date] > 5:
            alerts.append("Unusual frequency of transactions in category")
        # Suspicious merchant (first time seen)
        if merchant not in known_merchants:
            alerts.append("New/suspicious merchant detected")
            known_merchants.add(merchant)

        if alerts:
            txn_copy = txn.copy()
            txn_copy["alerts"] = alerts
            fraud_alerts.append(txn_copy)
    return fraud_alerts

@app.get("/fraud-detection")
def get_detect_fraud(transactions):
    transactions = generate_sms_data(50)
    for txn in transactions:
        txn["category"] = categorize_transaction(txn["merchant"], txn["type"])
    frauds = detect_fraud(transactions)
    return JSONResponse(content = {"fraud_alerts": frauds})

def generate_identity_fingerprint(transactions):
    fingerprint = {}
    # Spending distribution
    category_totals = defaultdict(int)
    total_debit = 0
    for txn in transactions:
        if txn["type"].lower() == "debit":
            category_totals[txn["category"]] += txn["amount"]
            total_debit += txn["amount"]
    
    fingerprint["spending_distribution"] = {cat: round(amount/total_debit*100, 1)
                                            for cat, amount in category_totals.items()}

    # Average transaction size
    debit_txns = [txn["amount"] for txn in transactions if txn["type"].lower() == "debit"]
    fingerprint["average_transaction"] = round(sum(debit_txns)/len(debit_txns), 2) if debit_txns else 0
    # Frequency per category
    freq_counter = defaultdict(int)
    for txn in transactions:
        freq_counter[txn["category"]] += 1
    fingerprint["frequency_per_category"] = dict(freq_counter)
    # Savings rate
    total_credit = sum(txn["amount"] for txn in transactions if txn["type"].lower() == "credit")
    fingerprint["savings_rate"] = round(((total_credit - total_debit)/total_credit)*100, 1) if total_credit > 0 else 0
    # Behavior trajectory
    behavior = defaultdict(list)
    for txn in transactions:
        if txn["type"].lower() == "debit":
            behavior[txn["category"]].append({"date": txn["date"], "amount": txn["amount"]})
    fingerprint["behavior_trajectory"] = dict(behavior)
    return fingerprint

@app.get("/identity-fingerprint")
def get_identity_fingerprint(transactions):
    transactions = generate_sms_data(50)
    for txn in transactions:
        txn["category"] = categorize_transaction(txn["merchant"], txn["type"])
    fingerprint = generate_identity_fingerprint(transactions)
    return JSONResponse(content = {"identity_fingerprint": fingerprint})

def forecast_by_category(transactions, days_ahead=7):
    df = pd.DataFrame(transactions)
    df["category"] = df["merchant"].apply(categorize_transaction)
    df["date"] = pd.to_datetime(df["date"])
    
    results = {}
    for category in df["category"].unique():
        cat_df = df[df["category"] == category].groupby("date")["amount"].sum().reset_index()
        cat_df = cat_df.sort_values("date")

        if len(cat_df) < 2: 
            continue

        # convert date to ordinal for regression
        X = np.array([d.toordinal() for d in cat_df["date"]]).reshape(-1, 1)
        y = cat_df["amount"].values

        model = LinearRegression()
        model.fit(X, y)

        future_dates = [cat_df["date"].max() + timedelta(days=i) for i in range(1, days_ahead+1)]
        X_future = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        y_future = model.predict(X_future)

        trend = "increasing" if model.coef_[0] > 0 else "decreasing"

        results[category] = {
            "trend": trend,
            "next_days": {d.strftime("%Y-%m-%d"): round(float(v), 2) for d, v in zip(future_dates, y_future)}
        }
    return results

@app.get("/forecast")
def get_forecast():
    transactions = generate_sms_data(100)
    forecast = forecast_by_category(transactions, days_ahead=7)
    return JSONResponse(content={"forecast": forecast})

#Financial Tip Generator
def financial_tips(df, income=50000, shopping_limit=10000):
    tips = []
    total_spent = df['Amount'].sum()
    savings = income - total_spent
    savings_rate = (savings / income) * 100

    # ---- CATEGORY-WISE RULES ---- #
    category_spend = df.groupby("Category")['Amount'].sum()

    # Food spending rule
    if "Food" in category_spend and (category_spend["Food"] / income) * 100 > 30:
        tips.append("🍲 Your food spending is quite high. Try home cooking twice a week.")

    # Entertainment upward trend (check last 2 months avg vs earlier)
    if "Entertainment" in df['Category'].unique():
        df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
        ent_monthly = df[df['Category'] == "Entertainment"].groupby('Month')['Amount'].sum()
        if len(ent_monthly) >= 2 and ent_monthly.iloc[-1] > ent_monthly.iloc[-2]:
            tips.append("🎬 Entertainment spending is increasing. Set a monthly cap for subscriptions.")

    # Utilities spike (compare last month to avg of earlier months)
    if "Utilities" in df['Category'].unique():
        util_monthly = df[df['Category'] == "Utilities"].groupby('Month')['Amount'].sum()
        if len(util_monthly) >= 2 and util_monthly.iloc[-1] > util_monthly.iloc[:-1].mean() * 1.3:
            tips.append("💡 Utility bills spiked. Consider energy-saving habits.")

    # Shopping threshold
    if "Shopping" in category_spend and category_spend["Shopping"] > shopping_limit:
        tips.append("🛍️ You’re spending a lot on shopping. Do you really need all those impulse buys?")

    # Savings rate rule
    if savings_rate < 20:
        tips.append("💰 Try saving at least 20% of income for future security.")

    return tips

tips = {
    "Food": [
        {"rule": lambda spend: spend > 0.3, "msg": "🍲 Your food spending is quite high. Try home cooking twice a week."}
    ],
    "Entertainment": [
        {"rule": lambda trend: trend == "up", "msg": "🎬 Entertainment spending is increasing. Set a monthly cap for subscriptions."}
    ],
    "Utilities": [
        {"rule": lambda spike: spike, "msg": "💡 Utility bills spiked. Consider energy-saving habits."}
    ],
    "Shopping": [
        {"rule": lambda spend: spend > 10000, "msg": "🛍️ You’re spending a lot on shopping. Do you really need all those impulse buys?"}
    ],
    "Savings": [
        {"rule": lambda rate: rate < 0.2, "msg": "💰 Try saving at least 20% of income for future security."}
    ]
}

@app.get("/tips/{category}")
def get_tip(category: str, spend: float = 0, trend: str = "flat", spike: bool = False, savings_rate: float = 0.3):
    category = category.capitalize()
    if category not in tips:
        return {"category": category, "tip": "No tips available for this category."}
    
    for rule in tips[category]:
        # apply the rule using relevant metric
        metric = spend if category in ["Food", "Shopping"] else (trend if category=="Entertainment" else (spike if category=="Utilities" else savings_rate))
        if rule["rule"](metric):
            return {"category": category, "tip": rule["msg"]}
    
    return {"category": category, "tip": "You're on track. Keep it up!"}

#Health Check
@app.get("/")
def read_root():
    return {"message": "Living Ledger Backend is running!"}



