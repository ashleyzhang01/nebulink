from pydantic import BaseModel

from app.schemas.linkedin_organization import LinkedinOrganization
from app.schemas.repository import Repository
from app.schemas.linkedin_user import LinkedinUser


class LinkedinQuerySchema(BaseModel):
    results: list[LinkedinOrganization]


class GeneralQuerySchema(BaseModel):
    search_type: str
    linkedin_results: list[LinkedinOrganization]
    linkedin_user_results: list[LinkedinUser]
    github_results: list[Repository]
