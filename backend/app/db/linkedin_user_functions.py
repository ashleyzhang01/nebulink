from typing import List, Tuple
from app.models.linkedin_user import LinkedinUser, LinkedinUserOrganizationMap
from app.schemas.linkedin_user import LinkedinUser as LinkedinUserSchema, LinkedinOrganizationContribution, LinkedinUserCreate
from app.schemas.linkedin_organization import LinkedinUserContribution
from sqlalchemy.orm import Session
import json
from cryptography.fernet import Fernet
from app.core.config import settings

def get_fernet():
    return Fernet(settings.LINKEDIN_PASSWORD_ENCRYPTION_KEY)


def get_user_organization_associations(db: Session, username: str = None, organization_id: str = None) -> List[Tuple[LinkedinOrganizationContribution, LinkedinUserContribution]]:
    query = db.query(LinkedinUserOrganizationMap)
    
    if username:
        query = query.filter(LinkedinUserOrganizationMap.linkedin_user_username == username).limit(500)
    if organization_id:
        query = query.filter(LinkedinUserOrganizationMap.linkedin_organization_id == organization_id).limit(500)
    
    associations = query.all()
    
    result = []
    for assoc in associations:
        org_contribution = LinkedinOrganizationContribution(
            linkedin_id=assoc.linkedin_organization_id,
            role=assoc.role,
            start_date=assoc.start_date.isoformat() if assoc.start_date else None,
            end_date=assoc.end_date.isoformat() if assoc.end_date else None
        )
        user_contribution = LinkedinUserContribution(
            username=assoc.linkedin_user_username,
            role=assoc.role,
            start_date=assoc.start_date.isoformat() if assoc.start_date else None,
            end_date=assoc.end_date.isoformat() if assoc.end_date else None
        )
        result.append((org_contribution, user_contribution))
    
    return result


def create_linkedin_user(linkedin_user: LinkedinUserSchema, db: Session):
    db_linkedin_user = LinkedinUser(
        username=linkedin_user.username,
        name=linkedin_user.name,
        header=linkedin_user.header,
        profile_picture=linkedin_user.profile_picture,
        email=linkedin_user.email,
        external_websites=json.dumps(linkedin_user.external_websites) if linkedin_user.external_websites else None,
    )
    db.add(db_linkedin_user)
    db.commit()
    db.refresh(db_linkedin_user)
    return db_linkedin_user

def get_linkedin_user_by_username(username: str, db: Session) -> LinkedinUserSchema:
    db_user = db.query(LinkedinUser).filter(LinkedinUser.username == username).first()
    if db_user:
        organizations = [org for org, _ in get_user_organization_associations(db, username=username)]
        user_dict = LinkedinUserSchema.from_orm(db_user).dict()
        user_dict['organizations'] = organizations
        return LinkedinUserSchema(**user_dict)
    return None

def update_linkedin_user(linkedin_user: LinkedinUserCreate, db: Session) -> LinkedinUserSchema | None:
    fernet = get_fernet()
    print("Linkedin user: ", linkedin_user)
    db_linkedin_user = db.query(LinkedinUser).filter(LinkedinUser.username == linkedin_user.username).first()
    if db_linkedin_user:
        update_data = linkedin_user.dict(exclude={'organizations'}, exclude_unset=True)
        for key, value in update_data.items():
            if key == 'external_websites':
                value = json.dumps(value) if value else None
            if key == 'password':
                value = fernet.encrypt(value.encode())
            setattr(db_linkedin_user, key, value)
        db.commit()
        db.refresh(db_linkedin_user)
        organizations = [
            LinkedinOrganizationContribution(
                linkedin_id=org_map.linkedin_organization_id,
                role=org_map.role,
                start_date=org_map.start_date.isoformat() if org_map.start_date else None,
                end_date=org_map.end_date.isoformat() if org_map.end_date else None
            ) for org_map in db_linkedin_user.organization_maps
        ]
        user_dict = LinkedinUserSchema.from_orm(db_linkedin_user).dict()
        user_dict['organizations'] = organizations
        return LinkedinUserSchema(**user_dict)
    return None