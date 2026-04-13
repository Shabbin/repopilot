from pathlib import Path
from git import Repo

BASE_REPOS_DIR = Path("cloned_repos")
BASE_REPOS_DIR.mkdir(exist_ok=True)


def clone_repository(repo_name: str, github_url: str) -> str:
    repo_path = BASE_REPOS_DIR / repo_name

    if repo_path.exists():
        return str(repo_path.resolve())

    Repo.clone_from(github_url, repo_path)
    return str(repo_path.resolve())