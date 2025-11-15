# app/db/goals.py
from app.core.firebase import db
from typing import Dict, List
from datetime import datetime

def set_goal(user_id: int, goal_name: str, target_amount: float):
    """
    Create or update a financial goal.
    """
    user_ref = db.collection('users').document(str(user_id))
    goal_ref = user_ref.collection('goals').document(goal_name.lower())
    goal_ref.set({
        'goal_name': goal_name,
        'target_amount': float(target_amount),
        'current_amount': 0.0,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })

def update_goal_progress(user_id: int, goal_name: str, amount: float):
    """
    Add progress to a goal.
    """
    user_ref = db.collection('users').document(str(user_id))
    goal_ref = user_ref.collection('goals').document(goal_name.lower())
    doc = goal_ref.get()
    if doc.exists:
        goal_data = doc.to_dict()
        current_amount = goal_data.get('current_amount', 0.0) + float(amount)
        goal_ref.update({
            'current_amount': current_amount,
            'updated_at': datetime.utcnow()
        })
    else:
        # If goal doesn't exist, create it with this amount as progress
        set_goal(user_id, goal_name, amount)
        update_goal_progress(user_id, goal_name, amount)

def get_goal(user_id: int, goal_name: str) -> Dict:
    """
    Get details of a specific goal.
    """
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.collection('goals').document(goal_name.lower()).get()
    return doc.to_dict() if doc.exists else {}

def get_all_goals(user_id: int) -> List[Dict]:
    """
    Get all goals for a user.
    """
    user_ref = db.collection('users').document(str(user_id))
    docs = user_ref.collection('goals').stream()
    return [doc.to_dict() for doc in docs]

def delete_goal(user_id: int, goal_name: str):
    """
    Delete a goal.
    """
    user_ref = db.collection('users').document(str(user_id))
    user_ref.collection('goals').document(goal_name.lower()).delete()
