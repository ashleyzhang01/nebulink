
from fastapi import APIRouter
from app.chromadb import get_chroma_collection
from app.agents.classifier import classify_query_func
from app.agents.company_query_optimizer import handle_company_query_func
from app.agents.other_query_optimizer import handle_other_query_func
from app.chromadb.dataclass import ChromaResult
from app.chromadb.internal_api import query_from_chroma
from app.db.linkedin_organization_functions import get_linkedin_organization_by_id
from app.models.linkedin_organization import LinkedinOrganization
from app.models.repository import Repository
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.search import GeneralQuerySchema, LinkedinQuerySchema
from app.utils.enums import ChromaCollections
from app.db.repository_functions import get_repository_by_path


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/perform_search", response_model=GeneralQuerySchema)
async def general_search(
    query: str,
    db: Session = Depends(get_db)
):
    print("entered general search func")
    
    classification = classify_query_func(query=query)
    github_results: list[Repository] = []

    if classification == "other":
        optimized_query = handle_other_query_func(query=query)
        print("Optimized query: ", optimized_query)

        github_chroma_results: list[ChromaResult] = query_from_chroma(
            query=optimized_query,
            collection=ChromaCollections.GITHUB_REPOSITORY,
            n_results=5,
        )
        print(github_chroma_results)
        for github_chroma_result in github_chroma_results:
            github_results.append(
                get_repository_by_path(
                    path=github_chroma_result.id,
                    db=db,
                )
            )
        
    optimized_query = handle_company_query_func(query=query)

    print("Optimized query: ", optimized_query)

    chroma_results = get_chroma_collection(ChromaCollections.LINKEDIN_ORGANIZATION).query(
        query_texts = optimized_query,
        n_results = 5
    )

    print(chroma_results)

    linkedin_results: list[LinkedinOrganization] = []
    # for chroma_result in chroma_results:
    #     linkedin_results.append(
    #         get_linkedin_organization_by_id(
    #             linkedin_id=chroma_result.id,
    #             db=db,
    #         )
    #     )
    # print(linkedin_results)
    github_results: list[Repository] = []

    return GeneralQuerySchema(linkedin_results=linkedin_results, github_results=github_results)

@router.get("/search_company", response_model=LinkedinQuerySchema)
async def linkedin_search(
    linkedin_user
):
    pass