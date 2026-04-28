import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    if not firebase_admin._apps:
        # Check if we should use a service account file or individual env vars
        firebase_creds_path = "firebase_credentials.json"
        
        if os.path.exists(firebase_creds_path):
            cred = credentials.Certificate(firebase_creds_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            }
            
            # Only initialize if we have at least project_id
            if cred_dict["project_id"]:
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            else:
                print("Warning: Firebase credentials not found. Auth will not work.")

def verify_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
