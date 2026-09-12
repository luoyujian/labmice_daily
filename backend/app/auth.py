import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.app.auth_database import get_auth_db
from backend.app.models.models import User

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
INSECURE_SECRET_KEYS = {"mouse-secret-key-2026", "changeme", "secret"}

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY", "").strip()
    if len(secret_key) < 32 or secret_key.lower() in INSECURE_SECRET_KEYS:
        raise RuntimeError("SECRET_KEY must be set to a strong, unique value of at least 32 characters")
    return secret_key

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_auth_db)) -> Optional[User]:
    """Returns User if token is valid, otherwise None"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    return user

def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Dependency that enforces authentication for all data viewing (guest or admin)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="系统数据受保护，请先登录账号后再查看",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_admin(user: User = Depends(require_auth)) -> User:
    """Dependency that enforces admin role"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可执行该修改/管理操作",
        )
    return user

def init_default_admin(db: Session):
    """Seed the initial administrator if it does not exist."""
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if not existing_admin:
        initial_password = os.getenv("ADMIN_PASSWORD", "").strip()
        if not initial_password or initial_password == "admin123":
            raise RuntimeError("ADMIN_PASSWORD must be set to a non-default value when creating the initial administrator")
        default_admin = User(
            username="admin",
            hashed_password=get_password_hash(initial_password),
            role="admin",
            display_name="系统管理员",
            is_active=True
        )
        db.add(default_admin)

    db.commit()
