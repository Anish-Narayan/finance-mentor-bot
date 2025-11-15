# app/db/users.py
from app.core.firebase import db
from datetime import datetime

def get_or_create_user(user_id: int, username: str):
    """Creates a user document if it doesn't exist, otherwise updates last active time."""
    user_ref = db.collection('users').document(str(user_id))
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        user_ref.set({
            'username': username,
            'created_at': datetime.utcnow(),
            'last_active': datetime.utcnow()
        })
        print(f"Created new user: {username} ({user_id})")
    else:
        user_ref.update({'last_active': datetime.utcnow()})
    
    return user_ref.get().to_dict()

def get_all_user_ids():
    """Returns a list of all user IDs from the database."""
    users_ref = db.collection('users').stream()
    return [user.id for user in users_ref]