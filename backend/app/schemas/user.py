from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    header: str | None = None
    summary: str | None = None
    github_user_id: Optional[str] = None
    linkedin_user_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    header: Optional[str] = None
    summary: Optional[str] = None
    github_user_id: Optional[str] = None
    linkedin_user_id: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
