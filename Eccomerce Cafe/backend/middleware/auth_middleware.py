from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_config import verify_token

security = HTTPBearer()

async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)):
    token = authorization.credentials
    decoded_token = verify_token(token)
    
    if not decoded_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Firebase token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return decoded_token
