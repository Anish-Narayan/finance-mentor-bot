# app/db/transactions.py
from app.core.firebase import db
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def add_transaction(user_id: int, amount: float, category: str, description: str, txn_type: str = "expense"):
    """
    Adds a transaction for a user.
    
    Args:
        user_id (int): Telegram user ID
        amount (float): Transaction amount
        category (str): Transaction category (e.g., groceries, salary)
        description (str): Original message/description
        txn_type (str): 'expense' or 'income'
    """
    if txn_type not in ["expense", "income"]:
        txn_type = "expense"

    user_ref = db.collection('users').document(str(user_id))
    user_ref.collection('transactions').add({
        "type": txn_type,
        "amount": float(amount),
        "category": category.lower(),
        "description": description,
        "timestamp": datetime.utcnow()
    })


async def get_transactions_for_period(user_id: int, days: int = 7) -> List[Dict]:
    """
    Fetches all transactions for a user in the last `days` days.

    Args:
        user_id (int): Telegram user ID
        days (int): Number of days to look back (default 7)

    Returns:
        List[Dict]: List of transactions
    """
    user_ref = db.collection('users').document(str(user_id))
    start_date = datetime.utcnow() - timedelta(days=days)

    # Use keyword arguments to avoid Firestore warning
    query = user_ref.collection('transactions').where(
        field_path="timestamp",
        op_string=">=",
        value=start_date
    ).stream()

    transactions = []
    for doc in query:
        txn = doc.to_dict()
        # Ensure each transaction has type, amount, and category
        txn.setdefault("type", "expense")
        txn.setdefault("amount", 0.0)
        txn.setdefault("category", "general")
        transactions.append(txn)

    return transactions


async def get_all_transactions(user_id: int) -> List[Dict]:
    """
    Fetches all transactions of a user (no time filter).

    Args:
        user_id (int): Telegram user ID

    Returns:
        List[Dict]: List of all transactions
    """
    user_ref = db.collection('users').document(str(user_id))
    query = user_ref.collection('transactions').stream()

    transactions = []
    for doc in query:
        txn = doc.to_dict()
        txn.setdefault("type", "expense")
        txn.setdefault("amount", 0.0)
        txn.setdefault("category", "general")
        transactions.append(txn)

    return transactions


async def get_balance(user_id: int) -> float:
    """
    Calculates user's current balance (income - expense).

    Args:
        user_id (int): Telegram user ID

    Returns:
        float: Balance amount
    """
    transactions = await get_all_transactions(user_id)
    balance = 0.0
    for txn in transactions:
        if txn["type"] == "income":
            balance += txn["amount"]
        else:
            balance -= txn["amount"]
    return balance


async def get_total_income(user_id: int, days: int = 7) -> float:
    """
    Total income in last `days` days.
    """
    transactions = await get_transactions_for_period(user_id, days)
    return sum(txn["amount"] for txn in transactions if txn["type"] == "income")


async def get_total_expense(user_id: int, days: int = 7) -> float:
    """
    Total expense in last `days` days.
    """
    transactions = await get_transactions_for_period(user_id, days)
    return sum(txn["amount"] for txn in transactions if txn["type"] == "expense")
