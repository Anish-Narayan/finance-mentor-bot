# app/db/budgets.py
from app.core.firebase import db
from typing import Dict, List
from datetime import datetime

def set_budget(user_id: int, category: str, amount: float):
    """
    Set or update a budget for a specific category.
    """
    user_ref = db.collection('users').document(str(user_id))
    budget_ref = user_ref.collection('budgets').document(category.lower())
    budget_ref.set({
        'amount': float(amount),
        'category': category.lower(),
        'created_at': datetime.utcnow()
    })

def get_budget(user_id: int, category: str) -> Dict:
    """
    Fetch budget for a specific category.
    """
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.collection('budgets').document(category.lower()).get()
    return doc.to_dict() if doc.exists else {}

def get_all_budgets(user_id: int) -> List[Dict]:
    """
    Fetch all budgets for a user.
    """
    user_ref = db.collection('users').document(str(user_id))
    docs = user_ref.collection('budgets').stream()
    return [doc.to_dict() for doc in docs]

def delete_budget(user_id: int, category: str):
    """
    Delete a budget for a specific category.
    """
    user_ref = db.collection('users').document(str(user_id))
    user_ref.collection('budgets').document(category.lower()).delete()
