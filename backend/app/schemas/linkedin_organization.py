import typing
from pydantic import BaseModel
from typing import Optional, List, Dict


if typing.TYPE_CHECKING:
    from app.schemas.linkedin_user import LinkedinUser


class LinkedinOrganizationBase(BaseModel):
    linkedin_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    specialties: Optional[str] = None
    logo: Optional[str] = None
    filters: Optional[Dict] = None


class LinkedinOrganizationCreate(LinkedinOrganizationBase):
    pass


class LinkedinOrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    specialties: Optional[str] = None
    logo: Optional[str] = None
    filters: Optional[Dict] = None


class LinkedinOrganization(LinkedinOrganizationBase):
    linkedin_users: List['LinkedinUser'] = []

    class Config:
        from_attributes = True
