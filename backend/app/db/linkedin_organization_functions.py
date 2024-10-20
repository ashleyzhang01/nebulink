from typing import Optional
from app.db.linkedin_user_functions import get_user_organization_associations
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_attribute
from app.chromadb import get_chroma_collection
from app.models.linkedin_organization import LinkedinOrganization
from app.models.linkedin_user import LinkedinUserOrganizationMap
from app.schemas.linkedin_organization import LinkedinOrganization as LinkedinOrganizationSchema
from datetime import datetime

from app.utils.enums import ChromaCollections

def get_linkedin_organization_by_id(linkedin_id: str, db: Session) -> LinkedinOrganizationSchema | None:
    db_organization = db.query(LinkedinOrganization).filter(LinkedinOrganization.linkedin_id == linkedin_id).first()
    if db_organization:
        linkedin_users = [user for _, user in get_user_organization_associations(db, organization_id=linkedin_id)]
        return LinkedinOrganizationSchema(
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
    return None

def create_linkedin_organization(organization: LinkedinOrganizationSchema, db: Session) -> LinkedinOrganizationSchema:
    # Create linkedin orgainzation in chroma
    try:
        name_string = f"Organization name: {organization.name}\n" if organization.name else ""
        description_string = f"Description: {organization.description}\n" if organization.description else ""
        industry_string = f"Industry: {organization.industry}\n" if organization.industry else ""
        company_size_string = f"Company size: {organization.company_size}\n" if organization.company_size else ""
        specialties_string = f"Specialties: {organization.specialties}\n" if organization.specialties else ""
        linkedin_chroma_string = (
            name_string + description_string + industry_string + company_size_string + specialties_string
        )
        linkedin_chroma_collection = get_chroma_collection(
            collection=ChromaCollections.LINKEDIN_ORGANIZATION,
        )
        linkedin_chroma_collection.upsert(
            documents=[linkedin_chroma_string],
            ids=[organization.linkedin_id],
        )
    except Exception as e:
        print(f"Error creating linkedin organization in chroma: {e}")
    # Create organization in DB
    db_organization = LinkedinOrganization(**organization.dict(exclude={'linkedin_users'}))
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return LinkedinOrganizationSchema(
        **db_organization.__dict__,
        linkedin_users=[]
    )

def update_linkedin_organization(organization: LinkedinOrganizationSchema, db: Session) -> LinkedinOrganizationSchema | None:
    db_organization = db.query(LinkedinOrganization).filter(LinkedinOrganization.linkedin_id == organization.linkedin_id).first()
    if db_organization:
        for key, value in organization.dict(exclude_unset=True).items():
            if key != 'linkedin_users':
                setattr(db_organization, key, value)
        db.commit()
        db.refresh(db_organization)
        return get_linkedin_organization_by_id(db_organization.linkedin_id, db)
    return None

def add_user_to_organization(linkedin_id: str, linkedin_username: str, role: Optional[str], start_date: Optional[datetime], end_date: Optional[datetime], db: Session) -> LinkedinOrganizationSchema | None:
    db_organization = db.query(LinkedinOrganization).filter(LinkedinOrganization.linkedin_id == linkedin_id).first()
    if db_organization:
        from app.db.linkedin_user_functions import get_linkedin_user_by_username
        db_linkedin_user = get_linkedin_user_by_username(linkedin_username, db)
        if db_linkedin_user:
            existing_relationship = db.query(LinkedinUserOrganizationMap).filter_by(
                linkedin_user_username=linkedin_username,
                linkedin_organization_id=linkedin_id
            ).first()

            if existing_relationship:
                set_attribute(existing_relationship, 'role', role)
                set_attribute(existing_relationship, 'start_date', start_date)
                set_attribute(existing_relationship, 'end_date', end_date)
            else:
                new_relationship = LinkedinUserOrganizationMap(
                    linkedin_user_username=linkedin_username,
                    linkedin_organization_id=linkedin_id,
                    role=role,
                    start_date=start_date,
                    end_date=end_date
                )
                db.add(new_relationship)
            
            db.commit()
            db.refresh(db_organization)
            return get_linkedin_organization_by_id(linkedin_id, db)
    return None