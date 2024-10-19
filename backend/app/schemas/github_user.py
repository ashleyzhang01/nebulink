from pydantic import BaseModel
from typing import Optional, List


class RepositoryContribution(BaseModel):
    path: str
    num_contributions: int


class GithubUserBase(BaseModel):
    username: str
    profile_picture: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    header: Optional[str] = None
    token: Optional[str] = None

class GithubUserCreate(GithubUserBase):
    pass

class GithubUser(GithubUserBase):
    repositories: List[RepositoryContribution] = []
    user_id: Optional[int] = None

    class Config:
        from_attributes = True