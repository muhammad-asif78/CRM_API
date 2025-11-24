import bcrypt
from datetime import datetime, timedelta

import dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
import os


load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY", "Super_Secret_Key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = int (os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 86400))

def hash_password(password: str) -> str:
    """
    hash password using bcrypt.
    Truncate to 72  bytes to avoid bcrypt issues.
    """
    if password is None:
        raise ValueError("Password cannot be None")
    password_bytes = password.encode("utf-8")[:72]      #UTF-8 is a standard encoding to convert text to bytes.
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")

def verify_password(plain_password: str,  hashed_password: str) -> bool:
    """
    verify password using bcrypt.
    :param plain_password:
    :param hashed_password:
    :return:
    """
    if not plain_password or not hashed_password:
        return False
    password_bytes = plain_password.encode("utf-8")[:72]
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    else:
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password)

def create_access_token(data: dict, expires_delta: int= ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def verify_token_role(token: str, allowed_roles: list) -> dict:
    payload = decode_access_token(token)
    role = payload.get("role")

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return payload
