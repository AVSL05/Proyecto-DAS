import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.mongodb_models import PasswordResetToken, User, UserRole
from .oauth_config import oauth
from .schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    TokenResponse,
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


async def get_current_user(request: Request) -> User:
    """Obtener el usuario actual autenticado"""
    token = get_bearer_token(request)

    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token invalido o expirado.")

    email = (payload.get("sub") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=401, detail="Token invalido.")

    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalido.")

    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    """Registrar un nuevo usuario"""
    try:
        email = payload.email.lower().strip()

        if payload.password != payload.confirm_password:
            raise HTTPException(status_code=400, detail="Las contrasenas no coinciden.")

        validate_password_strength(payload.password)
        phone = normalize_phone(payload.phone)

        # Verificar si el email ya existe
        existing = await User.find_one(User.email == email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya esta registrado.")

        # Crear nuevo usuario
        user = User(
            full_name=payload.full_name.strip(),
            email=email,
            phone=phone,
            password_hash=hash_password(payload.password),
            role=UserRole.CLIENT,
        )

        await user.insert()

        return RegisterResponse(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=normalize_role(user.role.value),
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en registro: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """Iniciar sesión"""
    email = payload.email.lower().strip()
    user = await User.find_one(User.email == email)

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas.")

    user_role = normalize_role(user.role.value)
    if payload.role != user_role:
        raise HTTPException(
            status_code=403,
            detail=f"Tu cuenta no tiene acceso de tipo '{payload.role}'.",
        )

    tok = create_access_token(subject=user.email, extra_claims={"uid": str(user.id), "role": user_role})

    return TokenResponse(
        token=tok["token"],
        token_type=tok["token_type"],
        expires_in=tok["expires_in"],
        user=UserOut(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user_role,
        ),
    )


@router.get("/me", response_model=UserOut)
async def me(request: Request):
    """Obtener información del usuario autenticado"""
    user = await get_current_user(request)
    return UserOut(
        id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=normalize_role(user.role.value),
    )


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    """Solicitar reseteo de contraseña"""
    email = payload.email.lower().strip()
    user = await User.find_one(User.email == email)

    if not user:
        return {"message": "Si el correo existe, te llegara un enlace para restablecer tu contrasena."}

    token = create_reset_token()
    token_h = hash_token(token)
    expires = reset_expiry_dt()

    # Marcar tokens anteriores como usados
    await PasswordResetToken.find(
        PasswordResetToken.user_id == str(user.id),
        PasswordResetToken.used == False,
    ).update({"$set": {"used": True}})

    # Crear nuevo token
    rec = PasswordResetToken(
        user_id=str(user.id),
        token_hash=token_h,
        expires_at=expires,
        used=False,
    )
    await rec.insert()

    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"
    print("\n[DEV] Password reset link:", reset_link, "\n")

    return {"message": "Si el correo existe, te llegara un enlace para restablecer tu contrasena."}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    """Resetear la contraseña usando el token"""
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Las contrasenas no coinciden.")

    validate_password_strength(payload.password)

    token_h = hash_token(payload.token)

    rec = await PasswordResetToken.find_one(PasswordResetToken.token_hash == token_h)

    if not rec or rec.used:
        raise HTTPException(status_code=400, detail="Token invalido o ya usado.")

    now = datetime.now(timezone.utc)
    if rec.expires_at < now:
        raise HTTPException(status_code=400, detail="Token expirado.")

    user = await User.get(rec.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Token invalido.")

    # Actualizar contraseña
    user.password_hash = hash_password(payload.password)
    await user.save()
    
    # Marcar token como usado
    rec.used = True
    await rec.save()

    return {"message": "Contrasena actualizada correctamente."}


@router.get("/google/login")
async def google_login(request: Request):
    """Iniciar login con Google OAuth"""
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    """Callback de Google OAuth"""
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

        # Buscar usuario por email o google_id
        user = await User.find_one({"$or": [{"email": email}, {"google_id": google_id}]})

        if user:
            # Actualizar información de Google
            if not user.google_id:
                user.google_id = google_id
            user.avatar_url = avatar_url
            user.full_name = full_name
            if not user.role:
                user.role = UserRole.CLIENT
            await user.save()
        else:
            # Crear nuevo usuario
            user = User(
                full_name=full_name,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
                phone=None,
                password_hash=None,
                role=UserRole.CLIENT,
            )
            await user.insert()

        user_role = normalize_role(user.role.value)
        access_token = create_access_token(
            subject=user.email,
            extra_claims={"uid": str(user.id), "role": user_role},
        )

        frontend_url = f"http://localhost:8000/login?token={access_token['token']}&provider=google"
        return RedirectResponse(url=frontend_url)

    except Exception as exc:
        print(f"Error en Google OAuth: {str(exc)}")
        raise HTTPException(status_code=400, detail=f"Error en autenticacion de Google: {str(exc)}")
