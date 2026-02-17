import re
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from datetime import datetime, timezone
from app.db_models import PasswordResetToken
from .schemas import ForgotPasswordRequest, ResetPasswordRequest
from .security import create_reset_token, hash_token, reset_expiry_dt
from .oauth_config import oauth

from .db import get_db
from app.db_models import User
from .schemas import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, UserOut
from .security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) < 8 or len(digits) > 15:
        raise HTTPException(status_code=400, detail="Teléfono inválido.")
    return digits

def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")
    if password.isalpha() or password.isnumeric():
        raise HTTPException(status_code=400, detail="La contraseña debe incluir letras y números.")

def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta token de autenticación.")
    return auth.split(" ", 1)[1].strip()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")

    validate_password_strength(payload.password)
    phone = normalize_phone(payload.phone)

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado.")

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    # Mensaje genérico para no filtrar si existe el correo
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    tok = create_access_token(subject=user.email, extra_claims={"uid": user.id})

    return TokenResponse(
        token=tok["token"],
        token_type=tok["token_type"],
        expires_in=tok["expires_in"],
        user=UserOut(id=user.id, full_name=user.full_name, email=user.email, phone=user.phone)
    )

@router.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    token = get_bearer_token(request)

    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    email = (payload.get("sub") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido.")

    return UserOut(id=user.id, full_name=user.full_name, email=user.email, phone=user.phone)

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    # Respuesta genérica para no filtrar si el correo existe
    if not user:
        return {"message": "Si el correo existe, te llegará un enlace para restablecer tu contraseña."}

    token = create_reset_token()
    token_h = hash_token(token)
    expires = reset_expiry_dt()

    # opcional: invalida tokens viejos sin usar
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})

    rec = PasswordResetToken(
        user_id=user.id,
        token_hash=token_h,
        expires_at=expires,
        used=False
    )
    db.add(rec)
    db.commit()

    # ✅ DEV: imprimimos el link (en prod aquí mandarías email)
    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"
    print("\n[DEV] Password reset link:", reset_link, "\n")

    return {"message": "Si el correo existe, te llegará un enlace para restablecer tu contraseña."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")

    validate_password_strength(payload.password)

    token_h = hash_token(payload.token)

    rec = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_h
    ).first()

    if not rec or rec.used:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado.")

    now = datetime.now(timezone.utc)
    if rec.expires_at < now:
        raise HTTPException(status_code=400, detail="Token expirado.")

    user = db.query(User).filter(User.id == rec.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido.")

    user.password_hash = hash_password(payload.password)
    rec.used = True

    db.commit()

    return {"message": "Contraseña actualizada correctamente."}


# ===== Google OAuth Endpoints =====

@router.get("/google/login")
async def google_login(request: Request):
    """Inicia el flujo de autenticación con Google"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Callback de Google OAuth - procesa la respuesta de Google"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="No se pudo obtener información del usuario de Google")
        
        email = user_info.get('email', '').lower().strip()
        google_id = user_info.get('sub')
        full_name = user_info.get('name', '')
        avatar_url = user_info.get('picture', '')
        
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Información de Google incompleta")
        
        # Buscar usuario existente por email o google_id
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        if user:
            # Actualizar información si el usuario ya existe
            if not user.google_id:
                user.google_id = google_id
            user.avatar_url = avatar_url
            user.full_name = full_name
        else:
            # Crear nuevo usuario
            user = User(
                full_name=full_name,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
                phone=None,  # No requerido para OAuth
                password_hash=None  # No necesario para OAuth
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Crear token JWT
        access_token = create_access_token(subject=user.email, extra_claims={"uid": user.id})
        
        # Redirigir al frontend con el token
        frontend_url = f"http://localhost:8000/login?token={access_token['token']}&provider=google"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        print(f"Error en Google OAuth: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error en autenticación de Google: {str(e)}")
