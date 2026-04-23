from sqlalchemy.orm import Session
from firebase_admin import auth, firestore
try:
    from repository import user_repository
    from schemas.user import UserCreate
except ImportError:
    from backend.repository import user_repository
    from backend.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    existing_user = user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")
    return user_repository.create_user(db=db, user=user)

def get_user_by_email(db: Session, email: str):
    user = user_repository.get_user_by_email(db, email)
    if not user:
        raise ValueError("User not found")
    return user

def get_all_firebase_users():
    # Fetch from Auth
    page = auth.list_users()
    users_list = []
    
    # Get Firestore reference
    db_fs = firestore.client()
    
    while page:
        for user in page.users:
            # Try to get extra info from Firestore
            doc_ref = db_fs.collection("users").document(user.uid)
            doc = doc_ref.get()
            
            user_data = {
                "id": user.uid,
                "email": user.email,
                "role": "COMPRADOR", # Default
                "is_active": True,
                "full_name": user.display_name
            }
            
            if doc.exists:
                fs_data = doc.to_dict()
                user_data.update(fs_data)
                
            users_list.append(user_data)
        page = page.get_next_page()
        
    return users_list

def save_user_profile(uid: str, profile_data: dict):
    db_fs = firestore.client()
    doc_ref = db_fs.collection("users").document(uid)
    # Merging data and ensuring is_active is set
    profile_data["is_active"] = profile_data.get("is_active", True)
    profile_data["createdAt"] = profile_data.get("createdAt", firestore.SERVER_TIMESTAMP)
    doc_ref.set(profile_data, merge=True)
    return {"status": "success"}

def upgrade_user_to_producer(uid: str, producer_data: dict):
    db_fs = firestore.client()
    doc_ref = db_fs.collection("users").document(uid)
    update_data = {
        **producer_data,
        "role": "PRODUCTOR",
        "is_active": True
    }
    doc_ref.set(update_data, merge=True)
    return {"status": "success"}

def get_user_profile_fs(uid: str):
    db_fs = firestore.client()
    doc = db_fs.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

import datetime

def create_product_fs(product_data: dict):
    db_fs = firestore.client()
    # Add timestamp as an ISO string to avoid FastAPI JSON serialization errors
    product_data["createdAt"] = datetime.datetime.utcnow().isoformat() + "Z"
    _, doc_ref = db_fs.collection("products").add(product_data)
    return {"id": doc_ref.id, **product_data}

def delete_product_fs(product_id: str):
    db_fs = firestore.client()
    db_fs.collection("products").document(product_id).delete()
    return {"status": "success"}

def get_all_products_fs():
    db_fs = firestore.client()
    docs = db_fs.collection("products").get()
    return [{"id": d.id, **d.to_dict()} for d in docs]
