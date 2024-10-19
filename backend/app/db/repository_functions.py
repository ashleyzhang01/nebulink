from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_attribute
from fastapi import Depends
from typing import List
from app.models.repository import Repository as RepositoryModel
from app.models.github_user import GithubUserRepositoryMap
from app.schemas.repository import Repository as RepositorySchema, GithubUserContribution
from app.db.session import get_db

def get_repository_by_path(path: str, db: Session = Depends(get_db)) -> RepositorySchema | None:
    db_repository = db.query(RepositoryModel).filter(RepositoryModel.path == path).first()
    if db_repository:
        github_users = [
            GithubUserContribution(
                username=user_repo_map.github_user_username,
                num_contributions=user_repo_map.num_contributions
            ) 
            for user_repo_map in db_repository.github_users
        ]
        return RepositorySchema(
            path=db_repository.path,
            description=db_repository.description,
            stars=db_repository.stars,
            github_users=github_users
        )
    return None

def get_all_repositories(db: Session) -> List[RepositorySchema]:
    db_repositories = db.query(RepositoryModel).all()
    return [
        RepositorySchema(
            path=repo.path,
            description=repo.description,
            stars=repo.stars,
            github_users=[
                GithubUserContribution(
                    username=user_repo_map.github_user_username,
                    num_contributions=user_repo_map.num_contributions
                ) for user_repo_map in repo.github_users
            ]
        ) for repo in db_repositories
    ]

def create_repository(repository: RepositorySchema, db: Session) -> RepositorySchema:
    db_repository = RepositoryModel(
        path=repository.path,
        description=repository.description,
        stars=repository.stars,
    )
    db.add(db_repository)
    db.commit()
    db.refresh(db_repository)
    return RepositorySchema(
        path=db_repository.path,
        description=db_repository.description,
        stars=db_repository.stars,
        github_users=[]
    )

def update_repository(repository: RepositorySchema, db: Session) -> RepositorySchema | None:
    db_repository = db.query(RepositoryModel).filter(RepositoryModel.path == repository.path).first()
    if db_repository:
        for key, value in repository.dict(exclude_unset=True).items():
            if key != 'github_users':
                setattr(db_repository, key, value)
        db.commit()
        db.refresh(db_repository)
        return get_repository_by_path(db_repository.path, db)
    return None

def add_user_to_repository(repository_path: str, github_username: str, num_contributions: int, db: Session) -> RepositorySchema | None:
    db_repository = db.query(RepositoryModel).filter(RepositoryModel.path == repository_path).first()
    if db_repository:
        from app.db.github_user_functions import get_github_user_by_username
        db_github_user = get_github_user_by_username(github_username, db)
        if db_github_user:
            existing_relationship = db.query(GithubUserRepositoryMap).filter_by(
                github_user_username=github_username,
                repository_path=repository_path
            ).first()

            if existing_relationship:
                set_attribute(existing_relationship, 'num_contributions', num_contributions)
            else:
                new_relationship = GithubUserRepositoryMap(
                    github_user_username=github_username,
                    repository_path=repository_path,
                    num_contributions=num_contributions
                )
                db.add(new_relationship)
            
            db.commit()
            db.refresh(db_repository)
            return get_repository_by_path(repository_path, db)
    return None
