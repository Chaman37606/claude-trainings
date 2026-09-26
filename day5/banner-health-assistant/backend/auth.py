"""JWT bearer authentication.

Password hashing uses `bcrypt` directly rather than `passlib` — passlib 1.7.4's bcrypt
backend is incompatible with bcrypt>=4.1 in this environment (raises `ValueError:
password cannot be longer than 72 bytes...` on every hash/verify call, a known
version-mismatch bug), so passlib is avoided entirely here even though it's installed.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import config
import crud
from database import get_db
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """Returns the `sub` (username) claim, or raises jwt exceptions on failure."""
    payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    return payload["sub"]


_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        username = decode_access_token(token)
    except jwt.PyJWTError:
        raise _CREDENTIALS_EXCEPTION
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise _CREDENTIALS_EXCEPTION
    return user
