from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import hashlib

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    # Step 1: SHA-256 hash (removes length limit issue)
    sha_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Step 2: bcrypt hash
    return pwd_context.hash(sha_hash)

def verify_password(plain, hashed):
    sha_hash = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(sha_hash, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)