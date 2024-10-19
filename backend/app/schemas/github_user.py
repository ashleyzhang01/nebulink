import typing
from pydantic import BaseModel
from typing import Optional, List

if typing.TYPE_CHECKING:
    from app.schemas.repository import Repository
    from app.schemas.user import User


class GithubUserBase(BaseModel):
    username: str
    profile_picture: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    header: Optional[str] = None


class GithubUserCreate(GithubUserBase):
    token: str


class GithubUserUpdate(BaseModel):
    profile_picture: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    header: Optional[str] = None
    token: Optional[str] = None


class GithubUserInDBBase(GithubUserBase):
    class Config:
        from_attributes = True


class GithubUser(GithubUserInDBBase):
    repositories: List['Repository'] = []
    user: Optional['User'] = None


class GithubUserInDB(GithubUserInDBBase):
    token: str
