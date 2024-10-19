import os
import re
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()


class GithubScraper:
    HEADERS: dict = {}

    def __init__(self, github_token: str | None = os.environ.get("GITHUB_TOKEN")):
        self.github_token = github_token
        if github_token:
            self.HEADERS = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

    def get_repo_info(self, repo_url: str) -> dict | None:
        """
        Get basic info on a repo
        """
        repo_response = requests.get(repo_url, headers=self.HEADERS)
        if repo_response.status_code == 200:
            repo_info = repo_response.json()
            return {
                "name": repo_info['name'],
                "description": repo_info['description'],
                "stars": repo_info['stargazers_count'],
                "url": repo_info['url']
            }

        else:
            print(f"Failed to fetch repo info: {repo_response.status_code}")
            return None

    def get_contributors(self, repo_url: str) -> list[dict] | None:
        contributors_response = requests.get(repo_url, headers=self.HEADERS)
        if contributors_response.status_code == 200:
            contributors = contributors_response.json()
            contributions = []
            for contributor in contributors:
                contribution = {
                    contributor['login']: {
                        "profile_picture": contributor["avatar_url"],
                        "num_contributions": contributor['contributions']
                    }
                }
                # Fetch user info to get their email (if public)
                user_url = contributor["url"]
                user_response = requests.get(user_url, headers=self.HEADERS)
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    contribution[contributor['login']]["name"] = user_info.get("name", "Name not available")
                    contribution[contributor['login']]["header"] = user_info.get("bio", "No bio available")
                    contribution[contributor['login']]["email"] = user_info.get("email", "Email not public")

                contributions.append(contribution)
            return contributions
        else:
            print(f"Failed to fetch contributors: {contributors_response.status_code}")
            print(contributors_response.json())
            return None

    def search_commits_by_user(self, username: str) -> set:
        """Search commits made by the user across all public repositories."""
        url = f"https://api.github.com/search/commits?q=author:{username}&per_page=100"
        contributions = set()

        while url:
            response = requests.get(url, headers=self.HEADERS)
            if response.status_code == 200:
                data = response.json()
                for item in data['items']:
                    repo_full_name = item['repository']['full_name']
                    contributions.add(repo_full_name)

                # pagination
                url = response.links.get('next', {}).get('url')
            else:
                print(f"Error: {response.status_code} - {response.json()}")
                break

        return contributions

    def fetch_pull_requests(self, repo: str, username: str) -> set:
        """Fetch pull requests opened by the user in the given repository."""
        url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100"
        contributions = set()

        while url:
            response = requests.get(url, headers=self.HEADERS)
            if response.status_code == 200:
                data = response.json()
                for pr in data:
                    if pr['user']['login'] == username:
                        contributions.add(repo)

                # pagination
                url = response.links.get('next', {}).get('url')
            else:
                print(f"Error fetching PRs for {repo}: {response.status_code}")
                break

        return contributions

    def fetch_all_contributions(self, username: str) -> tuple[str, list]:
        """Fetch all repositories a user has contributed to."""
        print(f"Searching for commits by {username}...")
        commit_repos = self.search_commits_by_user(username)

        all_repos = set(commit_repos)
        print(f"\nFound {len(commit_repos)} repositories with commits.")

        print("Fetching PR contributions...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.fetch_pull_requests, repo, username) for repo in commit_repos]
            for future in futures:
                all_repos.update(future.result())

        print(f"\n{username} has contributed to {len(all_repos)} repositories.")
        return (username, list(all_repos))

    def search_commit(self, username: str, repo: str) -> dict | None:
        """Search for commits made by a user in a specific repository."""
        url = f"https://api.github.com/repos/{repo}/commits?author={username}&per_page=1"
        while url:
            response = requests.get(url, headers=self.HEADERS)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Failed to fetch commits: {response.status_code}")
                break
        return None

    def get_email_from_patch(self, commit_url: str) -> str | None:
        """Fetch the patch of a commit and extract the author's email."""
        patch_url = f"{commit_url}.patch"
        response = requests.get(patch_url, headers=self.HEADERS)

        if response.status_code == 200:
            # Extract the email using regex from the patch content
            email_match = re.search(r'From:\s.*\s<([^>]+)>', response.text)
            if email_match:
                return email_match.group(1)
        return None

    def fetch_user_email(self, username: str, repo: str) -> str | None:
        print(f"Searching for commits by {username} in {repo}...")
        commit = self.search_commit(username, repo)
        if not commit:
            return None
        email = commit[0]["commit"]["author"]["email"]
        return email

    def search_commits_by_email(self, email: str) -> str:
        """Search commits using the author's email and return the GitHub username."""
        url = f"https://api.github.com/search/commits?q=author-email:{email}&sort=author-date&per_page=1"
        response = requests.get(url, headers=self.HEADERS)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.json()}")

        data = response.json()

        if data["total_count"] == 0:
            raise Exception(f"Couldn't find username for `{email}`")

        return data["items"][0]["author"]["login"]

    def get_username_from_email(self, email: str) -> str:
        """Fetch GitHub username by searching users or commits by email."""
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("A valid email address is required")

        # Search directly in user profiles (although not very reliable)
        url = f"https://api.github.com/search/users?q={email}+in:email"
        response = requests.get(url, headers=self.HEADERS)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.json()}")

        data = response.json()

        if data["total_count"] > 0:
            return data["items"][0]["login"]
        else:
            # Fallback to searching by commits if the email isn't found in profiles
            return self.search_commits_by_email(email)
