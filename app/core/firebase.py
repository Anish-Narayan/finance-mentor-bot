# app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings

def initialize_firebase():
    """Initializes the Firebase Admin SDK."""
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.FIREBASE_PROJECT_ID,
            })
            print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        exit(1)

# Call initialization once
initialize_firebase()

# Get a reference to the Firestore database
db = firestore.client()