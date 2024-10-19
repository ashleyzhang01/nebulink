from typing import Optional, Set
from app.utils.github_scraper import GithubScraper
from app.schemas import GithubUser as GithubUserSchema, Repository as RepositorySchema
from app.db.github_user_functions import get_github_user_by_username, update_github_user, create_github_user
from app.db.repository_functions import add_user_to_repository, get_repository_by_path, create_repository, update_repository
from sqlalchemy.orm import Session


def get_github_user_2_degree_network(username: str, token: Optional[str], db: Session):
    github_scraper = GithubScraper(token)
    processed_users: Set[str] = set()
    processed_repos: Set[str] = set()

    # if not github_user.email:
    #     github_user.email = github_scraper.fetch_user_email(user_contributions[0][0], user_contributions[1][0])
    #     update_github_user(github_user)
    
    def process_user_network(username, depth=0):
        if depth > 2 or username in processed_users:  # Stop at 2nd degree
            return
        
        try:
            user_contributions = github_scraper.fetch_all_contributions(username)
            db_github_user = get_github_user_by_username(username, db)
            
            if not db_github_user:
                db_github_user = create_github_user(GithubUserSchema(username=username), db)
            
            for repo_path in user_contributions[1]:
                if repo_path in processed_repos:
                    continue

                try:
                    db_repository = get_repository_by_path(repo_path, db)

                    repo_info = github_scraper.get_repo_info(f"https://api.github.com/repos/{repo_path}")
                    if not repo_info:
                        continue

                    processed_repos.add(repo_path)
                    repo_schema = RepositorySchema(
                        path=repo_path,
                        description=repo_info["description"],
                        stars=repo_info["stars"]
                    )
                    
                    if not db_repository:
                        db_repository = create_repository(repo_schema, db)
                    elif db_repository.description != repo_info["description"] or db_repository.stars != repo_info["stars"]:
                        db_repository = update_repository(repo_schema, db)
                    
                    add_user_to_repository(repo_path, db_github_user.username, 0, db)

                    contributors_url = f"https://api.github.com/repos/{repo_path}/contributors"
                    contributors = github_scraper.get_contributors(contributors_url)

                    for contributor in contributors:
                        contributor_username = list(contributor.keys())[0]
                        contributor_info = contributor[contributor_username]
                        
                        if contributor_username in processed_users:
                            continue

                        processed_users.add(contributor_username)
                        db_contributor = get_github_user_by_username(contributor_username, db)
                        contributor_schema = GithubUserSchema(
                            username=contributor_username,
                            profile_picture=contributor_info["profile_picture"],
                            name=contributor_info["name"],
                            email=contributor_info["email"],
                            header=contributor_info["header"]
                        )

                        if not db_contributor:
                            db_contributor = create_github_user(contributor_schema, db)
                        elif (db_contributor.profile_picture != contributor_info["profile_picture"] or
                                db_contributor.name != contributor_info["name"] or
                                db_contributor.email != contributor_info["email"] or
                                db_contributor.header != contributor_info["header"]):
                            update_github_user(contributor_schema, db)

                        add_user_to_repository(db_repository.path, db_contributor.username, contributor_info["num_contributions"], db)
                        
                        if depth < 1:
                            process_user_network(contributor_username, depth + 1)

                except Exception as e:
                    print(f"Error processing repository {repo_path}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error processing user network: {e}")
    process_user_network(username)


# def get_github_user_1_degree_network(github_user: GithubUserSchema, github_scraper: GithubScraper):
#     contributions = github_scraper.fetch_all_contributions(github_user.username)
#     network = {}
#     for repo in contributions[1][:2]: # for ease of testing, as we don't cache or store yet
#         print(f"repo: {repo}")
#         contributors_url = f"https://api.github.com/repos/{repo}/contributors"
#         contributors = github_scraper.get_contributors(contributors_url)[:2] # for ease of testing, as we don't cache or store yet
#         repo_info = github_scraper.get_repo_info(f"https://api.github.com/repos/{repo}")
#         db_repository = get_repository_by_path(repo)
#         if not db_repository:
#             db_repository = create_repository(
#                 RepositorySchema(
#                     path=repo, 
#                     user_ids=list(set([github_user.id] + [user.id for user in contributors])), 
#                     description=repo_info["description"], 
#                     stars=repo_info["stars"]
#                 )
#             )
#         else:
#             db_repository = update_repository(
#                 RepositorySchema(path=repo, description=repo_info["description"], stars=repo_info["stars"])
#             )
#             for k, in contributors:
#                 add_user_to_repository(db_repository, user)
#         network[repo] = {"people": contributors, "info": repo_info}
#     return network

# def get_second_degree_network(username):
#   contributions = fetch_all_contributions(username)
#   print(contributions)
#   network = {}
#   for repo in contributions[1][:2]: # for ease of testing, as we don't cache or store yet
#     contributors_url = f"https://api.github.com/repos/{repo}/contributors"
#     contributors = get_contributors(contributors_url)[:2] # for ease of testing, as we don't cache or store yet
#     for contributor in contributors:
#       contributor_network = get_first_degree_network(list(contributor.keys())[0])
#       contributor["network"] = contributor_network
#     repo_info = get_repo_info(f"https://api.github.com/repos/{repo}")
#     network[repo] = {"people": contributors, "info": repo_info}
#   return network
