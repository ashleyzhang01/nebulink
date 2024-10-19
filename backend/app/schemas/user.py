from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    header: str | None = None
    summary: str | None = None
    github_user: str | None = None
    linkedin_user: str | None = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    header: str | None = None
    summary: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str