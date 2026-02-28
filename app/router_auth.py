import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db_models import PasswordResetToken, User, UserRole
from .db import get_db
from .oauth_config import oauth
from .schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserOut,
)
from .security import (
    create_access_token,
    create_reset_token,
    decode_access_token,
    hash_password,
    hash_token,
    reset_expiry_dt,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])
VALID_ROLES = {UserRole.CLIENT.value, UserRole.ADMIN.value}


def normalize_role(role: Optional[str]) -> str:
    role_value = (role or UserRole.CLIENT.value).strip().lower()
    if role_value not in VALID_ROLES:
        return UserRole.CLIENT.value
    return role_value


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) < 8 or len(digits) > 15:
        raise HTTPException(status_code=400, detail="Telefono invalido.")
    return digits


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 8 caracteres.")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="La contrasena no debe superar 72 bytes (aprox. 72 caracteres).",
        )
    if password.isalpha() or password.isnumeric():
        raise HTTPException(status_code=400, detail="La contrasena debe incluir letras y numeros.")


def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta token de autenticacion.")
    return auth.split(" ", 1)[1].strip()


def get_current_user(request: Request, db: Session) -> User:
    token = get_bearer_token(request)

    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token invalido o expirado.")

    email = (payload.get("sub") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=401, detail="Token invalido.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token invalido.")

    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Las contrasenas no coinciden.")

    validate_password_strength(payload.password)
    phone = normalize_phone(payload.phone)

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya esta registrado.")

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=hash_password(payload.password),
        role=UserRole.CLIENT.value,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=normalize_role(user.role),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")

    user_role = normalize_role(user.role)

    tok = create_access_token(subject=user.email, extra_claims={"uid": user.id, "role": user_role})

    return TokenResponse(
        token=tok["token"],
        token_type=tok["token_type"],
        expires_in=tok["expires_in"],
        user=UserOut(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user_role,
        ),
    )


@router.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return UserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=normalize_role(user.role),
    )


@router.patch("/me", response_model=UserOut)
def update_profile(
    payload: UpdateProfileRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    
    if payload.full_name is not None:
        full_name = payload.full_name.strip()
        if len(full_name) < 3 or len(full_name) > 120:
            raise HTTPException(status_code=400, detail="El nombre debe tener entre 3 y 120 caracteres.")
        user.full_name = full_name
    
    if payload.phone is not None:
        phone = normalize_phone(payload.phone)
        user.phone = phone
    
    db.commit()
    db.refresh(user)
    
    return UserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=normalize_role(user.role),
    )


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    
    # Verificar que el usuario tenga contraseña (no usuarios de Google)
    if not user.password_hash:
        raise HTTPException(
            status_code=400,
            detail="Esta cuenta usa inicio de sesión con Google y no tiene contraseña."
        )
    
    # Verificar contraseña actual
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")
    
    # Verificar que las nuevas contraseñas coincidan
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas nuevas no coinciden.")
    
    # Validar fortaleza de la nueva contraseña
    validate_password_strength(payload.new_password)
    
    # Actualizar contraseña
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    
    return {"message": "Contraseña actualizada correctamente."}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"message": "Si el correo existe, te llegara un enlace para restablecer tu contrasena."}

    token = create_reset_token()
    token_h = hash_token(token)
    expires = reset_expiry_dt()

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False,
    ).update({"used": True})

    rec = PasswordResetToken(
        user_id=user.id,
        token_hash=token_h,
        expires_at=expires,
        used=False,
    )
    db.add(rec)
    db.commit()

    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"
    print("\n[DEV] Password reset link:", reset_link, "\n")

    return {"message": "Si el correo existe, te llegara un enlace para restablecer tu contrasena."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Las contrasenas no coinciden.")

    validate_password_strength(payload.password)

    token_h = hash_token(payload.token)

    rec = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_h).first()

    if not rec or rec.used:
        raise HTTPException(status_code=400, detail="Token invalido o ya usado.")

    now = datetime.now(timezone.utc)
    if rec.expires_at < now:
        raise HTTPException(status_code=400, detail="Token expirado.")

    user = db.query(User).filter(User.id == rec.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token invalido.")

    user.password_hash = hash_password(payload.password)
    rec.used = True
    db.commit()

    return {"message": "Contrasena actualizada correctamente."}


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="No se pudo obtener informacion del usuario de Google")

        email = user_info.get("email", "").lower().strip()
        google_id = user_info.get("sub")
        full_name = user_info.get("name", "")
        avatar_url = user_info.get("picture", "")

        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Informacion de Google incompleta")

        user = db.query(User).filter((User.email == email) | (User.google_id == google_id)).first()

        if user:
            if not user.google_id:
                user.google_id = google_id
            user.avatar_url = avatar_url
            user.full_name = full_name
            if not user.role:
                user.role = UserRole.CLIENT.value
        else:
            user = User(
                full_name=full_name,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
                phone=None,
                password_hash=None,
                role=UserRole.CLIENT.value,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        user_role = normalize_role(user.role)
        access_token = create_access_token(
            subject=user.email,
            extra_claims={"uid": user.id, "role": user_role},
        )

        frontend_url = f"http://localhost:8000/login?token={access_token['token']}&provider=google"
        return RedirectResponse(url=frontend_url)

    except Exception as exc:
        print(f"Error en Google OAuth: {str(exc)}")
        raise HTTPException(status_code=400, detail=f"Error en autenticacion de Google: {str(exc)}")
