from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class GithubUserRepositoryMap(Base):
    __tablename__ = "github_user_repository_map"

    github_user_username = Column(String, ForeignKey("github_users.username"), primary_key=True)
    repository_path = Column(String, ForeignKey("repositories.path"), primary_key=True)
    num_contributions = Column(Integer, default=0)

    github_user = relationship("GithubUser", back_populates="repository_maps")
    repository = relationship("Repository", back_populates="github_users")


class GithubUser(Base):
    __tablename__ = "github_users"

    username = Column(String, primary_key=True, index=True)
    profile_picture = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    header = Column(String, nullable=True)
    token = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="github_user", uselist=False)
    repository_maps = relationship("GithubUserRepositoryMap", back_populates="github_user")
