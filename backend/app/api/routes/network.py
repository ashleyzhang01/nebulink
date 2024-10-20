from app.db.linkedin_user_functions import get_linkedin_user_by_username, get_user_organization_associations
from app.db.github_user_functions import get_github_user_by_username, get_github_users_by_repository
from app.db.repository_functions import get_all_repositories, get_repositories_by_github_user, get_repository_by_path
from app.db.linkedin_organization_functions import get_linkedin_organization_by_id
from app.db.user_functions import get_current_user, get_user_by_id
from app.models.linkedin_organization import LinkedinOrganization
from app.schemas.linkedin_organization import LinkedinOrganization as LinkedinOrganizationSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from typing import Dict, List
from app.utils.github_scraper import GithubScraper

router = APIRouter(prefix="/network", tags=["network"])

@router.get("")
async def get_user_network(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await get_user_network(current_user.id, db)

@router.get("/public")
async def get_public_network(db: Session = Depends(get_db)):
    return await get_public_network(db)

def get_associated_github_user(user_id: int, db: Session):
    user = get_user_by_id(user_id, db)
    return user.github_user if user else None

def get_associated_linkedin_user(user_id: int, db: Session):
    user = get_user_by_id(user_id, db)
    return user.linkedin_user if user else None

async def get_user_network(user_id: int, db: Session) -> Dict[str, List]:
    user = get_user_by_id(user_id, db)
    if not user:
        return {"nodes": [], "groups": []}

    nodes = []
    groups = []
    processed_users = set()
    github_scraper = GithubScraper()

    def create_node(user, is_linkedin, connection_order, group_id):
        node = {
            "id": len(nodes),
            "is_linkedin": is_linkedin,
            "username": user.username,
            "individual_name": user.name,
            "header": user.header,
            "email": user.email,
            "profile_picture": user.profile_picture,
            "link": f"https://{'www.linkedin.com/in' if is_linkedin else 'github.com'}/{user.username}/",
            "connection_order": connection_order,
            "corresponding_user_nodes": [],
            "group_id": group_id
        }
        nodes.append(node)
        return node

    def process_linkedin_user(linkedin_user, connection_order=0):
        if linkedin_user.username in processed_users:
            return None

        processed_users.add(linkedin_user.username)
        user_nodes = []

        # Process organizations
        for org_contribution, _ in get_user_organization_associations(db, username=linkedin_user.username):
            org = get_linkedin_organization_by_id(org_contribution.linkedin_id, db)
            if org:
                node = create_node(linkedin_user, True, connection_order, org.linkedin_id)
                user_nodes.append(node)
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

        # Check for corresponding GitHub user
        github_user = get_associated_github_user(linkedin_user.user_id, db)
        if github_user:
            github_nodes = process_github_user(github_user, connection_order)
            if github_nodes:
                for linkedin_node in user_nodes:
                    for github_node in github_nodes:
                        linkedin_node["corresponding_user_nodes"].append(github_node["id"])
                        github_node["corresponding_user_nodes"].append(linkedin_node["id"])

        return user_nodes

    def process_github_user(github_user, connection_order=0):
        if github_user.username in processed_users:
            return None

        processed_users.add(github_user.username)
        user_nodes = []

        # Process repositories
        for repo in get_repositories_by_github_user(github_user.username, db):
            node = create_node(github_user, False, connection_order, repo.path)
            user_nodes.append(node)
            if repo.path not in [g["id"] for g in groups]:
                groups.append({
                    "id": repo.path,
                    "name": repo.path.split('/')[-1],
                    "description": repo.description,
                    "is_linkedin": False,
                    "stars": repo.stars,
                    "link": f"https://github.com/{repo.path}"
                })

        linkedin_user = get_associated_linkedin_user(github_user.user_id, db)
        if linkedin_user:
            linkedin_nodes = process_linkedin_user(linkedin_user, connection_order)
            if linkedin_nodes:
                for github_node in user_nodes:
                    for linkedin_node in linkedin_nodes:
                        github_node["corresponding_user_nodes"].append(linkedin_node["id"])
                        linkedin_node["corresponding_user_nodes"].append(github_node["id"])

        return user_nodes

    # Process the main user and their direct associations
    linkedin_user = get_associated_linkedin_user(user_id, db)
    github_user = get_associated_github_user(user_id, db)

    if linkedin_user:
        process_linkedin_user(linkedin_user)
    if github_user:
        process_github_user(github_user)

    # Process second-degree connections
    first_degree_nodes = [node for node in nodes if node["connection_order"] == 0]
    for node in first_degree_nodes:
        if node["is_linkedin"]:
            linkedin_user = get_linkedin_user_by_username(node["username"], db)
            for org_contribution, _ in get_user_organization_associations(db, username=linkedin_user.username):
                for _, user_contribution in get_user_organization_associations(db, organization_id=org_contribution.linkedin_id):
                    other_user = get_linkedin_user_by_username(user_contribution.username, db)
                    if other_user:
                        nodes.extend(process_linkedin_user(other_user, 2) or [])
        else:
            github_user = get_github_user_by_username(node["username"], db)
            for repo in get_repositories_by_github_user(github_user.username, db):
                for other_user in get_github_users_by_repository(repo.path, db):
                    nodes.extend(process_github_user(other_user, 2) or [])

    return {"nodes": nodes, "groups": groups}


async def get_public_network(db: Session) -> Dict[str, List]:
    nodes = []
    links = []
    processed_groups = set()

    def process_linkedin_organization(org_id):
        if org_id in processed_groups:
            return

        processed_groups.add(org_id)
        org = get_linkedin_organization_by_id(org_id, db)
        if not org:
            return

        node = {
            "id": org_id,
            "type": "linkedin_organization",
            "name": org.name,
            "description": org.description,
            "industry": org.industry,
            "company_size": org.company_size,
            "user_count": len(org.linkedin_users)
        }
        nodes.append(node)

        # Process connections to other organizations
        for user_contribution in org.linkedin_users:
            user_orgs = get_user_organization_associations(db, username=user_contribution.username)
            for other_org, _ in user_orgs:
                if other_org.linkedin_id != org_id:
                    links.append({
                        "source": org_id,
                        "target": other_org.linkedin_id,
                        "type": "shared_user"
                    })
                    process_linkedin_organization(other_org.linkedin_id)

    def process_github_repository(repo_path):
        if repo_path in processed_groups:
            return

        processed_groups.add(repo_path)
        repo = get_repository_by_path(repo_path, db)
        if not repo:
            return

        node = {
            "id": repo_path,
            "type": "github_repository",
            "name": repo_path.split('/')[-1],
            "description": repo.description,
            "stars": repo.stars,
            "contributor_count": len(repo.github_users)
        }
        nodes.append(node)

        # Process connections to other repositories
        for user_contribution in repo.github_users:
            user_repos = get_repositories_by_github_user(user_contribution.username, db)
            for other_repo in user_repos:
                if other_repo.path != repo_path:
                    links.append({
                        "source": repo_path,
                        "target": other_repo.path,
                        "type": "shared_contributor"
                    })
                    process_github_repository(other_repo.path)

    # Start processing from all LinkedIn organizations
    linkedin_organizations = db.query(LinkedinOrganization).offset(0).limit(500).all()
    
    if not linkedin_organizations:
        raise HTTPException(status_code=404, detail="No LinkedIn organizations found")
    
    linkedin_organizations = [LinkedinOrganizationSchema.from_orm(org) for org in linkedin_organizations]
    for org in linkedin_organizations:
        process_linkedin_organization(org.linkedin_id)

    for repo in get_all_repositories(db):
        process_github_repository(repo.path)

    return {"nodes": nodes, "links": links}