from pydantic import BaseModel
from typing import Optional, List

from app.schemas.linkedin_organization import LinkedinOrganization
from app.schemas.repository import Repository


class LinkedinQuerySchema(BaseModel):
    results: list[LinkedinOrganization]


class GeneralQuerySchema(BaseModel):
    linkedin_results: list[LinkedinOrganization]
    github_results: list[Repository]
