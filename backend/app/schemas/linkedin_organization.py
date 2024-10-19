import typing
from pydantic import BaseModel
from typing import Optional, List, Dict


class LinkedinUserContribution(BaseModel):
    username: str
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


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
    linkedin_users: List[LinkedinUserContribution] = []

    class Config:
        from_attributes = True
