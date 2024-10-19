from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    header = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    github_user_id = Column(String, ForeignKey("github_users.username"), nullable=True)
    linkedin_user_id = Column(String, ForeignKey("linkedin_users.username"), nullable=True)

    github_user = relationship("GithubUser", back_populates="user")
    linkedin_user = relationship("LinkedinUser", back_populates="user")
