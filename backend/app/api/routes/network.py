from app.agents.github_scraper_agent_helper import get_github_user_2_degree_network
from app.agents.linkedin_scraper_agent_helper import get_linkedin_user_2_degree_network
from app.db.linkedin_user_functions import get_linkedin_user_by_username, get_user_organization_associations, update_linkedin_user
from app.db.github_user_functions import get_github_user_by_username, get_github_users_by_repository
from app.db.repository_functions import get_repositories_by_github_user
from app.db.linkedin_organization_functions import get_linkedin_organization_by_id
from app.schemas.linkedin_user import LinkedinOrganizationContribution, LinkedinUserInDB
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, LinkedinUser, LinkedinOrganization
from app.schemas import LinkedinUserCreate, LinkedinUser as LinkedinUserSchema, LinkedinOrganization as LinkedinOrganizationSchema
from app.db.user_functions import get_current_user
from app.agents.scraper_agents import LinkedinRequest, Response
from typing import Dict, List
from app.utils.github_scraper import GithubScraper

router = APIRouter(prefix="/network", tags=["network"])


@router.get("")
async def get_user_network(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_network(current_user.id, db)

def get_user_network(user_id: int, db: Session) -> Dict[str, List]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"nodes": [], "groups": []}

    nodes = []
    groups = []
    processed_users = set()
    github_scraper = GithubScraper()

    def process_linkedin_user(linkedin_user, connection_order=0):
        if linkedin_user.username in processed_users:
            return

        processed_users.add(linkedin_user.username)
        node = {
            "id": len(nodes),
            "is_linkedin": True,
            "username": linkedin_user.username,
            "individual_name": linkedin_user.name,
            "header": linkedin_user.header,
            "email": linkedin_user.email,
            "profile_picture": linkedin_user.profile_picture,
            "link": f"https://www.linkedin.com/in/{linkedin_user.username}/",
            "connection_order": connection_order,
            "corresponding_user_nodes": []
        }

        # Check for corresponding GitHub user
        if linkedin_user.email:
            try:
                github_username = github_scraper.get_username_from_email(linkedin_user.email)
                github_user = get_github_user_by_username(github_username, db)
                if github_user:
                    github_node = process_github_user(github_user, connection_order)
                    node["corresponding_user_nodes"].append(github_node["id"])
                    github_node["corresponding_user_nodes"].append(node["id"])
            except Exception:
                pass

        nodes.append(node)

        # Process organizations
        for org_contribution, _ in get_user_organization_associations(db, username=linkedin_user.username):
            org = get_linkedin_organization_by_id(org_contribution.linkedin_id, db)
            if org:
                node["group_id"] = org.linkedin_id
                if org.linkedin_id not in [g["id"] for g in groups]:
                    groups.append({
                        "id": org.linkedin_id,
                        "name": org.name,
                        "description": org.description,
                        "logo": org.logo,
                        "link": org.website,
                        "industry": org.industry,
                        "company_size": org.company_size,
                        "headquarters": org.headquarters,
                        "specialties": org.specialties,
                        "is_linkedin": True
                    })

                # Process other users in the organization
                if connection_order < 2:
                    for _, user_contribution in get_user_organization_associations(db, organization_id=org.linkedin_id):
                        other_user = get_linkedin_user_by_username(user_contribution.username, db)
                        if other_user:
                            process_linkedin_user(other_user, connection_order + 1)

    def process_github_user(github_user, connection_order=0):
        if github_user.username in processed_users:
            return

        processed_users.add(github_user.username)
        node = {
            "id": len(nodes),
            "is_linkedin": False,
            "username": github_user.username,
            "individual_name": github_user.name,
            "header": github_user.header,
            "email": github_user.email,
            "profile_picture": github_user.profile_picture,
            "link": f"https://github.com/{github_user.username}",
            "connection_order": connection_order,
            "corresponding_user_nodes": []
        }

        nodes.append(node)

        # Process repositories
        for repo in get_repositories_by_github_user(github_user.username, db):
            node["group_id"] = repo.path
            if repo.path not in [g["id"] for g in groups]:
                groups.append({
                    "id": repo.path,
                    "name": repo.path.split('/')[-1],
                    "description": repo.description,
                    "is_linkedin": False,
                    "stars": repo.stars,
                    "link": f"https://github.com/{repo.path}"
                })

            # Process other users in the repository
            if connection_order < 2:
                for other_user in get_github_users_by_repository(repo.path, db):
                    process_github_user(other_user, connection_order + 1)

    # Start processing from the user's LinkedIn and GitHub profiles
    if user.linkedin_user:
        process_linkedin_user(user.linkedin_user)
    if user.github_user:
        process_github_user(user.github_user)

    return {"nodes": nodes, "groups": groups}