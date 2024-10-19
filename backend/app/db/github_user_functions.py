from app.models.github_user import GithubUser
from app.schemas.github_user import RepositoryContribution
from sqlalchemy.orm import Session
from app.schemas import GithubUser as GithubUserSchema, Repository as RepositorySchema


def create_github_user(github_user: GithubUserSchema, db: Session):
    db_github_user = GithubUser(
        username=github_user.username,
        profile_picture=github_user.profile_picture,
        name=github_user.name,
        email=github_user.email,
        header=github_user.header,
        token=github_user.token,
    )
    db.add(db_github_user)
    db.commit()
    db.refresh(db_github_user)
    return db_github_user


def get_github_user_by_username(username: str, db: Session) -> GithubUserSchema:
    db_user = db.query(GithubUser).filter(GithubUser.username == username).first()
    if db_user:
        repositories = [
            RepositoryContribution(
                path=repo_map.repository.path,
                num_contributions=repo_map.num_contributions
            ) for repo_map in db_user.repository_maps
        ]
        user_dict = GithubUserSchema.from_orm(db_user).dict()
        user_dict['repositories'] = repositories
        return GithubUserSchema(**user_dict)
    return None


def update_github_user(github_user: GithubUserSchema, db: Session) -> GithubUserSchema | None:
    db_github_user = db.query(GithubUser).filter(GithubUser.username == github_user.username).first()
    if db_github_user:
        update_data = github_user.dict(exclude={'repositories'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_github_user, key, value)
        db.commit()
        db.refresh(db_github_user)
        # Convert the repositories to RepositorySchema
        repositories = [
            RepositoryContribution(
                path=repo_map.repository.path,
                num_contributions=repo_map.num_contributions
            ) for repo_map in db_github_user.repository_maps
        ]
        user_dict = GithubUserSchema.from_orm(db_github_user).dict()
        user_dict['repositories'] = repositories
        return GithubUserSchema(**user_dict)
    return None
