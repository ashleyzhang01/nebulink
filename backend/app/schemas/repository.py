from pydantic import BaseModel
from typing import Optional, List


class GithubUserContribution(BaseModel):
    username: str
    num_contributions: int


class RepositoryBase(BaseModel):
    path: str
    description: Optional[str] = None
    stars: int = 0


class RepositoryCreate(RepositoryBase):
    pass

class Repository(RepositoryBase):
    github_users: List[GithubUserContribution] = []

    class Config:
        from_attributes = True
