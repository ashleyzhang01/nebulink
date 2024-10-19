from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    path = Column(String, primary_key=True, index=True)
    description = Column(String, nullable=True)
    stars = Column(Integer, default=0)

    github_users = relationship("GithubUser", secondary="github_user_repository_map", back_populates="repositories")
