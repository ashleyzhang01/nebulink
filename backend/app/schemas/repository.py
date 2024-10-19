import typing
from pydantic import BaseModel
from typing import Optional, List

if typing.TYPE_CHECKING:
    from app.schemas.github_user import GithubUser


class RepositoryBase(BaseModel):
    path: str
    description: Optional[str] = None
    stars: int = 0


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryUpdate(BaseModel):
    description: Optional[str] = None
    stars: Optional[int] = None


class Repository(RepositoryBase):
    github_users: List['GithubUser'] = []

    class Config:
        from_attributes = True
