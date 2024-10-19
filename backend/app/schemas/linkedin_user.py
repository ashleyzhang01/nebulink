import typing
from pydantic import BaseModel, validator
from typing import Optional, List
import json

if typing.TYPE_CHECKING:
    from app.schemas.user import User


class LinkedinOrganizationContribution(BaseModel):
    linkedin_id: str
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class LinkedinUserBase(BaseModel):
    username: str
    name: Optional[str] = None
    header: Optional[str] = None
    profile_picture: Optional[str] = None
    email: Optional[str] = None
    external_websites: Optional[List[str]] = None

    @validator('external_websites', pre=True)
    def parse_external_websites(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        json_encoders = {
            list: lambda v: json.dumps(v)
        }


class LinkedinUserCreate(LinkedinUserBase):
    email: str
    password: Optional[str] = None


class LinkedinUser(LinkedinUserBase):
    organizations: List[LinkedinOrganizationContribution] = []
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class LinkedinUserUpdate(BaseModel):
    name: Optional[str] = None
    header: Optional[str] = None
    profile_picture: Optional[str] = None
    email: Optional[str] = None
    external_websites: Optional[List[str]] = None
    password: Optional[str] = None


class LinkedinUserInDB(LinkedinUser):
    password: str
