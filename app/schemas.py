from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

UserRole = Literal["cliente", "administrativo"]

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int | str  # SQLite usa int y MongoDB usa ObjectId (string)
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole = "cliente"

class RegisterResponse(UserOut):
    pass

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    role: Optional[UserRole] = None

class TokenResponse(BaseModel):
    token: str
    token_type: str
    expires_in: int
    user: UserOut

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10, max_length=500)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=120)
    phone: Optional[str] = Field(None, min_length=8, max_length=30)

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
