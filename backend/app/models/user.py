from sqlalchemy import Column, Integer, String
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    header = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    # TODO: add fk to github user and linkedin user