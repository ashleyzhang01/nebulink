from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class LinkedinUserOrganizationMap(Base):
    __tablename__ = "linkedin_user_organization_map"

    linkedin_user_username = Column(String, ForeignKey("linkedin_users.username"), primary_key=True)
    linkedin_organization_id = Column(String, ForeignKey("linkedin_organizations.linkedin_id"), primary_key=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    role = Column(String, nullable=True)

    linkedin_user = relationship("LinkedinUser", back_populates="organization_maps")
    linkedin_organization = relationship("LinkedinOrganization", back_populates="user_maps")


class LinkedinUser(Base):
    __tablename__ = "linkedin_users"

    username = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    header = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    email = Column(String, nullable=True)
    external_websites = Column(String, nullable=True)  # Store as JSON string
    password = Column(String, nullable=True)  # hashed

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="linkedin_user", uselist=False)
    organizations = relationship("LinkedinOrganization", secondary="linkedin_user_organization_map", back_populates="linkedin_users")
