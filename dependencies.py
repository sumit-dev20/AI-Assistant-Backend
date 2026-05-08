# app/auth/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt_handler import decode_jwt  

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        user_id = decode_jwt(token)  
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))