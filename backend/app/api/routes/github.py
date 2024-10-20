from app.db.github_user_functions import update_github_user
from app.agents.github_scraper_agent_helper import get_github_user_2_degree_network
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, GithubUser
from app.schemas import GithubUserCreate, GithubUser as GithubUserSchema, Repository as RepositorySchema
from app.db.user_functions import get_current_user
from app.db.repository_functions import get_all_repositories
from app.agents.scraper_agents import GithubRequest
from uagents.query import query
import json
from typing import List

router = APIRouter(prefix="/github", tags=["github"])

GITHUB_AGENT_ADDRESS = "agent1qfa7t0jmvkl7s5y2namkxhu3xeyc8w9wdc8nszqdza37e8lq5vj5q6aq0cm"

async def agent_query(req: GithubRequest):
    print("Github agent address: ", GITHUB_AGENT_ADDRESS)
    response = await query(destination=GITHUB_AGENT_ADDRESS, message=req, timeout=15.0)
    data = json.loads(response.decode_payload())
    return data["text"]


@router.post("/create", response_model=GithubUserSchema)
async def create_github_user(
    github_user: GithubUserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the GitHub user already exists for the current user
    existing_github_user = db.query(GithubUser).filter(
        GithubUser.username == github_user.username,
    ).first()
    print("Existing github user: ", existing_github_user)

    if existing_github_user and existing_github_user.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="GitHub user already exists for this user")

    if existing_github_user:
        # update user id association
        existing_github_user.user_id = current_user.id
        existing_github_user.token = github_user.token
        db.commit()
        db.refresh(existing_github_user)
        new_github_user = existing_github_user
    else:
        new_github_user = GithubUser(
            username=github_user.username,
            token=github_user.token,
            user_id=current_user.id
        )
        db.add(new_github_user)
        db.commit()
        db.refresh(new_github_user)

    try:
        get_github_user_2_degree_network(new_github_user.username, new_github_user.token, db)
        # req = GithubRequest(
        #     username=new_github_user.username,
        #     token=new_github_user.token,
        # )
        # res = await agent_query(req)
        # if res != "success":
        #     raise HTTPException(status_code=500, detail="Agent processing failed")
    except Exception as e:
        db.delete(new_github_user)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error calling agent: {str(e)}")

    return new_github_user


@router.post("/sync/{github_username}", response_model=GithubUserSchema)
async def sync_github_user(
    github_username: str,
    db: Session = Depends(get_db)
):
    existing_github_user = db.query(GithubUser).filter(
        GithubUser.username == github_username,
    ).first()

    if not existing_github_user:
        raise HTTPException(status_code=404, detail="GitHub user not found")
    
    try:
        get_github_user_2_degree_network(existing_github_user.username, existing_github_user.token, db)
        # req = GithubRequest(
        #     username=existing_github_user.username,
        #     token=existing_github_user.token,
        # )
        # res = await agent_query(req)
        # if res != "success":
        #     raise HTTPException(status_code=500, detail="Agent processing failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling agent: {str(e)}")

    return existing_github_user


@router.put("/update", response_model=GithubUserSchema)
async def update_github_user_info(
    github_user_update: GithubUserCreate,
    db: Session = Depends(get_db)
):
    github_user_update_dict = github_user_update.dict()
    print("Github user update dict: ", github_user_update_dict)
    github_user = db.query(GithubUser).filter(
        GithubUser.username == github_user_update_dict["username"],
    ).first()
    if not github_user:
        raise HTTPException(status_code=404, detail="GitHub user not found")
    for key, value in github_user_update_dict.items():
        if value is not None:
            setattr(github_user, key, value)
    db.commit()
    db.refresh(github_user)
    return github_user


@router.get("/repositories", response_model=List[RepositorySchema])
async def get_all_repos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all repositories stored in the database.
    """
    repositories = get_all_repositories(db)
    return repositories