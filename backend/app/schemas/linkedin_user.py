import typing
from pydantic import BaseModel, validator
from typing import Optional, List
import json

if typing.TYPE_CHECKING:
    from app.schemas.linkedin_organization import LinkedinOrganization
    from app.schemas.user import User


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
    password: str


class LinkedinUserUpdate(BaseModel):
    name: Optional[str] = None
    header: Optional[str] = None
    profile_picture: Optional[str] = None
    email: Optional[str] = None
    external_websites: Optional[List[str]] = None
    password: Optional[str] = None


class LinkedinUser(LinkedinUserBase):
    organizations: List['LinkedinOrganization'] = []
    user: Optional['User'] = None

    class Config:
        from_attributes = True


class LinkedinUserInDB(LinkedinUser):
    password: str
