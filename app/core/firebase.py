# app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from app.core.config import settings

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    Tries to use credentials from an environment variable (for production).
    If that fails, falls back to the service account file (for local dev).
    """
    try:
        if not firebase_admin._apps:
            # For Vercel/Production: Read from environment variable
            firebase_creds_json = os.getenv('FIREBASE_CREDS_JSON')
            if firebase_creds_json:
                print("Initializing Firebase from environment variable...")
                cred_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(cred_dict)
            # For Local Development: Read from file
            else:
                print("Initializing Firebase from file...")
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_FILE)
            
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        exit(1)

# Call initialization once when the module is loaded
initialize_firebase()

# Get a reference to the Firestore database
db = firestore.client()