from app.agents.linkedin_scraper_agent_helper import get_linkedin_user_2_degree_network
from app.db.linkedin_user_functions import get_user_organization_associations, update_linkedin_user
from app.schemas.linkedin_user import LinkedinOrganizationContribution
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, LinkedinUser, LinkedinOrganization
from app.schemas import LinkedinUserCreate, LinkedinUser as LinkedinUserSchema, LinkedinOrganization as LinkedinOrganizationSchema
from app.db.user_functions import get_current_user
from app.agents.scraper_agents import LinkedinRequest
from uagents.query import query
import json
from typing import List
from cryptography.fernet import Fernet
from app.core.config import settings

router = APIRouter(prefix="/linkedin", tags=["linkedin"])

LINKEDIN_AGENT_ADDRESS = "agent1qfa7t0jmvkl7s5y2namkxhu3xeyc8w9wdc8nszqdza37e8lq5vj5q6aq0cm"

def get_fernet():
    return Fernet(settings.LINKEDIN_PASSWORD_ENCRYPTION_KEY)

async def agent_query(req: LinkedinRequest):
    print("Linkedin agent address: ", LINKEDIN_AGENT_ADDRESS)
    response = await query(destination=LINKEDIN_AGENT_ADDRESS, message=req, timeout=15.0)
    data = json.loads(response.decode_payload())
    return data["text"]


@router.post("/create", response_model=LinkedinUserSchema)
async def create_linkedin_user(
    linkedin_user: LinkedinUserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the Linkedin user already exists for the current user
    existing_linkedin_user = db.query(LinkedinUser).filter(
        LinkedinUser.username == linkedin_user.username,
    ).first()

    if existing_linkedin_user and existing_linkedin_user.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Linkedin user already exists for this user")

    fernet = get_fernet()
    encrypted_password = fernet.encrypt(linkedin_user.password.encode())
    if existing_linkedin_user:
        # update user id association
        existing_linkedin_user.user_id = current_user.id
        existing_linkedin_user.password = encrypted_password
        db.commit()
        db.refresh(existing_linkedin_user)
        new_linkedin_user = existing_linkedin_user
    else:
        new_linkedin_user = LinkedinUser(
            username=linkedin_user.username,
            email=linkedin_user.email,
            password=encrypted_password,
            user_id=current_user.id
        )
        db.add(new_linkedin_user)
        db.commit()
        db.refresh(new_linkedin_user)

    try:
        decrypted_password = None
        if new_linkedin_user.password:
            decrypted_password = fernet.decrypt(new_linkedin_user.password).decode()
        get_linkedin_user_2_degree_network(new_linkedin_user.email, decrypted_password, db)
        # req = LinkedinRequest(
        #     username=new_linkedin_user.username,
        #     password=new_linkedin_user.password,
        # )
        # res = await agent_query(req)
        # if res != "success":
        #     raise HTTPException(status_code=500, detail="Agent processing failed")
    except Exception as e:
        db.delete(new_linkedin_user)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error calling agent: {str(e)}")

    return new_linkedin_user


@router.post("/sync/{linkedin_username}", response_model=LinkedinUserSchema)
async def sync_linkedin_user(
    linkedin_username: str,
    db: Session = Depends(get_db)
):
    existing_linkedin_user = db.query(LinkedinUser).filter(LinkedinUser.username == linkedin_username).first()

    if not existing_linkedin_user:
        raise HTTPException(status_code=404, detail="Linkedin user not found")

    try:
        decrypted_password = None
        if existing_linkedin_user.password:
            fernet = get_fernet()
            decrypted_password = fernet.decrypt(existing_linkedin_user.password).decode()
        get_linkedin_user_2_degree_network(existing_linkedin_user.email, decrypted_password, db)
        # req = LinkedinRequest(
        #     email=existing_linkedin_user.email,
        #     password=existing_linkedin_user.password,
        # )
        # res = await agent_query(req)
        # if res != "success":
        #     raise HTTPException(status_code=500, detail="Agent processing failed")

        db.refresh(existing_linkedin_user)
        
        # Convert to Pydantic model for response
        organizations = [
            LinkedinOrganizationContribution(
                linkedin_id=org_map.linkedin_organization_id,
                role=org_map.role,
                start_date=org_map.start_date,
                end_date=org_map.end_date
            ) for org_map in existing_linkedin_user.organization_maps
        ]
        
        return LinkedinUserSchema(
            username=existing_linkedin_user.username,
            name=existing_linkedin_user.name,
            header=existing_linkedin_user.header,
            profile_picture=existing_linkedin_user.profile_picture,
            email=existing_linkedin_user.email,
            external_websites=existing_linkedin_user.external_websites,
            organizations=organizations,
            user_id=existing_linkedin_user.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling agent: {str(e)}")

    return existing_linkedin_user


@router.get("/organizations", response_model=List[LinkedinOrganizationSchema])
async def get_all_linkedin_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all LinkedIn organizations.
    
    This endpoint returns a list of all LinkedIn organizations in the database.
    It supports pagination through skip and limit parameters.
    """
    organizations = db.query(LinkedinOrganization).offset(skip).limit(limit).all()
    
    if not organizations:
        raise HTTPException(status_code=404, detail="No LinkedIn organizations found")
    
    return [LinkedinOrganizationSchema.from_orm(org) for org in organizations]


@router.get("/users", response_model=List[LinkedinUserSchema])
async def get_all_linkedin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all LinkedIn users.
    
    This endpoint returns a list of all LinkedIn users in the database.
    It supports pagination through skip and limit parameters.
    """
    users = db.query(LinkedinUser).offset(skip).limit(limit).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="No LinkedIn users found")
    
    result = []
    for user in users:
        organizations = [org for org, _ in get_user_organization_associations(db, username=user.username)]
        user_dict = LinkedinUserSchema.from_orm(user).dict()
        user_dict['organizations'] = organizations
        result.append(LinkedinUserSchema(**user_dict))
    
    return result