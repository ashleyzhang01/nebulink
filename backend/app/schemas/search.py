from pydantic import BaseModel

from app.schemas.linkedin_organization import LinkedinOrganization
from app.schemas.repository import Repository


class LinkedinQuerySchema(BaseModel):
    results: list[LinkedinOrganization]


class GeneralQuerySchema(BaseModel):
    search_type: str
    linkedin_results: list[LinkedinOrganization]
    github_results: list[Repository]
