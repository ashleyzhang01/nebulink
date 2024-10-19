from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_attribute
from app.models.linkedin_organization import LinkedinOrganization
from app.models.linkedin_user import LinkedinUserOrganizationMap
from app.schemas.linkedin_organization import LinkedinOrganization as LinkedinOrganizationSchema, LinkedinUserContribution
from datetime import datetime

def get_linkedin_organization_by_id(linkedin_id: str, db: Session) -> LinkedinOrganizationSchema | None:
    db_organization = db.query(LinkedinOrganization).filter(LinkedinOrganization.linkedin_id == linkedin_id).first()
    if db_organization:
        linkedin_users = [
            LinkedinUserContribution(
                username=user_org_map.linkedin_user_username,
                role=user_org_map.role,
                start_date=user_org_map.start_date.isoformat() if user_org_map.start_date else None,
                end_date=user_org_map.end_date.isoformat() if user_org_map.end_date else None
            ) 
            for user_org_map in db_organization.user_maps
        ]
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

def add_user_to_organization(linkedin_id: str, linkedin_username: str, role: str, start_date: str, end_date: str, db: Session) -> LinkedinOrganizationSchema | None:
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
                set_attribute(existing_relationship, 'start_date', datetime.fromisoformat(start_date) if start_date else None)
                set_attribute(existing_relationship, 'end_date', datetime.fromisoformat(end_date) if end_date else None)
            else:
                new_relationship = LinkedinUserOrganizationMap(
                    linkedin_user_username=linkedin_username,
                    linkedin_organization_id=linkedin_id,
                    role=role,
                    start_date=datetime.fromisoformat(start_date) if start_date else None,
                    end_date=datetime.fromisoformat(end_date) if end_date else None
                )
                db.add(new_relationship)
            
            db.commit()
            db.refresh(db_organization)
            return get_linkedin_organization_by_id(linkedin_id, db)
    return None