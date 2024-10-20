
from fastapi import APIRouter

from app.agents.classifier import classify_query_func
from app.agents.company_query_optimizer import handle_company_query_func
from app.agents.other_query_optimizer import handle_other_query_func
from app.chromadb import get_chroma_collection
from app.chromadb.dataclass import ChromaResult
from app.chromadb.internal_api import query_from_chroma
from app.db.linkedin_organization_functions import get_linkedin_organization_by_id
from app.db.linkedin_user_functions import get_users_by_organization
from app.models.linkedin_organization import LinkedinOrganization
from app.schemas.linkedin_organization import LinkedinOrganization as LinkedinOrganizationSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from typing import Dict, List
from app.schemas.search import GeneralQuerySchema, LinkedinQuerySchema
from app.utils.enums import ChromaCollections
from app.utils.github_scraper import GithubScraper


router = APIRouter(prefix="/network", tags=["network"])


@router.get("/search", response_model=GeneralQuerySchema)
async def general_search(
    query: str,
    db: Session = Depends(get_db)
):
    classification = classify_query_func(query=query)
    if classification == "other":
        optimized_query = handle_other_query_func(query=query)
        chroma_client = get_chroma_collection(collection=ChromaCollections.GITHUB_REPOSITORY)
        # TODO: github case
        
    
    # Linkedin case
    optimized_query = handle_company_query_func(query=query)
    chroma_results: list[ChromaResult] = query_from_chroma(
        query=optimized_query,
        n_results=5,
        collection=ChromaCollections.LINKEDIN_ORGANIZATION,
    )
    linkedin_results: list[LinkedinOrganization] = []
    for chroma_result in chroma_results:
        linkedin_results.append(
            get_linkedin_organization_by_id(
                linkedin_id=chroma_result.id,
                db=db,
            )
        )


    # Query from chroma using the classification and the optimized query
    



@router.get("/search_company", response_model=LinkedinQuerySchema)
async def linkedin_search(
    linkedin_user
):
    pass