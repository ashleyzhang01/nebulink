from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class LinkedinOrganization(Base):
    __tablename__ = "linkedin_organizations"

    linkedin_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    headquarters = Column(String, nullable=True)
    specialties = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    filters = Column(JSON, nullable=True)

    linkedin_users = relationship("LinkedinUserOrganizationMap", back_populates="linkedin_organization")
