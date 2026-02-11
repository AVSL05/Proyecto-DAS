import os
import time
from typing import Optional, Dict, Any
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 JWT settings (para dev; en prod esto va en variables de entorno)
JWT_SECRET = os.getenv("JWT_SECRET", "DEV_CHANGE_ME_SUPER_SECRET")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "3600"))  # 1 hora

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    now = int(time.time())
    exp = now + JWT_TTL_SECONDS
    payload = {
        "sub": subject,   # normalmente el email o user_id
        "iat": now,
        "exp": exp,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return {"token": token, "token_type": "bearer", "expires_in": JWT_TTL_SECONDS}

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise ValueError("Token inválido o expirado")

RESET_TTL_MINUTES = int(os.getenv("RESET_TTL_MINUTES", "15"))

def create_reset_token() -> str:
    # token “adivinable = NO”: suficientemente largo
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def reset_expiry_dt() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=RESET_TTL_MINUTES)
