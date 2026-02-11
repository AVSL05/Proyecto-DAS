from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str

class RegisterResponse(UserOut):
    pass

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

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
