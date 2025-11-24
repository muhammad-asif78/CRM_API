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


