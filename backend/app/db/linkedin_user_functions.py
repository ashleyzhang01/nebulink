from app.models.linkedin_user import LinkedinUser, LinkedinUserOrganizationMap
from app.schemas.linkedin_user import LinkedinUser as LinkedinUserSchema, LinkedinOrganizationContribution
from sqlalchemy.orm import Session
import json
from cryptography.fernet import Fernet
from app.core.config import settings


fernet = Fernet(settings.LINKEDIN_PASSWORD_ENCRYPTION_KEY)


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
        organizations = [
            LinkedinOrganizationContribution(
                linkedin_id=org_map.linkedin_organization_id,
                role=org_map.role,
                start_date=org_map.start_date.isoformat() if org_map.start_date else None,
                end_date=org_map.end_date.isoformat() if org_map.end_date else None
            ) for org_map in db_user.organization_maps
        ]
        user_dict = LinkedinUserSchema.from_orm(db_user).dict()
        user_dict['organizations'] = organizations
        return LinkedinUserSchema(**user_dict)
    return None

def update_linkedin_user(linkedin_user: LinkedinUserSchema, db: Session) -> LinkedinUserSchema | None:
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