
from fastapi import APIRouter
from app.chromadb import get_chroma_collection
from app.agents.classifier import classify_query_func
from app.agents.company_query_optimizer import handle_company_query_func
from app.agents.other_query_optimizer import handle_other_query_func
from app.chromadb.dataclass import ChromaResult
from app.chromadb.internal_api import query_from_chroma
from app.db.linkedin_organization_functions import get_linkedin_organization_by_id
from app.models.linkedin_organization import LinkedinOrganization
from app.models.linkedin_user import LinkedinUser
from app.models.repository import Repository
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.search import GeneralQuerySchema, LinkedinQuerySchema
from app.utils.enums import ChromaCollections
from app.db.repository_functions import get_repository_by_path
from app.db.linkedin_user_functions import get_users_by_organization


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/perform_search", response_model=GeneralQuerySchema)
async def general_search(
    query: str,
    db: Session = Depends(get_db)
):
    print("entered general search func")

    print(get_chroma_collection(ChromaCollections.LINKEDIN_ORGANIZATION).count())
    print(get_chroma_collection(ChromaCollections.GITHUB_REPOSITORY).count())
    
    classification = classify_query_func(query=query)
    github_results: list[Repository] = []
    print(classification)

    #if we're just searching over individual, search over github and linkedin companies
    if classification == "individual":
        optimized_query = handle_other_query_func(query=query)
        print("Optimized query: ", optimized_query)

        github_chroma_results = get_chroma_collection(ChromaCollections.GITHUB_REPOSITORY).query(
            query_texts = optimized_query,
            n_results = 5
        )

        print(github_chroma_results)

        for github_chroma_result_id in github_chroma_results.get('ids')[0]:
            github_results.append(
                get_repository_by_path(
                    path=github_chroma_result_id,
                    db=db,
                )
            )
    #if we're searching over companies, search over linkedin companies
        
    optimized_query = handle_company_query_func(query=query)

    print("Optimized query: ", optimized_query)

    chroma_results = get_chroma_collection(ChromaCollections.LINKEDIN_ORGANIZATION).query(
        query_texts = optimized_query,
        n_results = 5
    )

    print(get_chroma_collection(ChromaCollections.LINKEDIN_ORGANIZATION).count())
    print(get_chroma_collection(ChromaCollections.GITHUB_REPOSITORY).count())

    print(chroma_results)

    linkedin_results: list[LinkedinOrganization] = []
    linkedin_user_results: list[LinkedinUser] = []


    for chroma_result_id in chroma_results.get('ids')[0]:
        linkedin_results.append(
            get_linkedin_organization_by_id(
                linkedin_id=chroma_result_id,
                db=db,
            )
        )
        users = get_users_by_organization(
            db=db,
            organization_id=chroma_result_id,
        )
        for user in users:
            linkedin_user_results.append(user)

    print("linkedin: ", linkedin_results)
    print("github: ", github_results)

    return GeneralQuerySchema(search_type=classification, linkedin_results=linkedin_results, linkedin_user_results=linkedin_user_results, github_results=github_results)

"""
resulting:
search_type = "individual" or "company"
linkedin_results = list of LinkedinOrganizationSchema(
            linkedin_id=db_organization.linkedin_id,
            name=db_organization.name,
            description=db_organization.description,
            website=db_organization.website,
            industry=db_organization.industry,
            company_size=db_organization.company_size,
            headquarters=db_organization.headquarters,
            specialties=db_organization.specialties,
            logo=db_organization.logo,
            filters=db_organization.filters,
            linkedin_users=linkedin_users
        )
github_results = list of RepositorySchema(
            path=db_repository.path,
            description=db_repository.description,
            stars=db_repository.stars,
            github_users=github_users
        )
"""

@router.get("/search_company", response_model=LinkedinQuerySchema)
async def linkedin_search(
    linkedin_user
):
    pass