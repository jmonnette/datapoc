from github import Github
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
g = Github(os.getenv("GITHUB_TOKEN"))  # Get GitHub access token from environment variable

def _diff_shas(sha1, sha2, repo):
    compare = repo.compare(sha1, sha2)
    for file in compare.files:
        yield  { "filename": file.filename, "patch": file.patch }

def diff_shas(sha1, sha2, repo_username, repo_name):
    repo = g.get_repo(f"{repo_username}/{repo_name}")  # get repository using user and repository name
    return _diff_shas(sha1, sha2, repo)
        
def diff_commits(commit1, commit2, repo_username, repo_name):
    repo = g.get_repo(f"{repo_username}/{repo_name}")  # get repository using user and repository name
    return _diff_shas(commit1.sha, commit2.sha, repo)

def diff_tags(tag1, tag2, repo_username, repo_name):
    repo = g.get_repo(f"{repo_username}/{repo_name}")  # get repository using user and repository name

    tags = repo.get_tags() 

    sha1 = ""
    sha2 = ""
    for tag in tags:
        if tag.name == tag1:
            sha1 = tag.commit.sha
        elif tag.name == tag2:
            sha2 = tag.commit.sha

    if sha1 and sha2:
        return _diff_shas(sha1, sha2, repo)


if __name__ == "__main__":
    # Get parameters from command line
    repo_username = sys.argv[1]
    repo_name     = sys.argv[2]
    tag1          = sys.argv[3]
    tag2          = sys.argv[4]

    diffs = diff_tags(tag1, tag2, repo_username, repo_name)

    for diff in diffs:
        print(f"Filename : {diff['filename']}\nPatch : {diff['patch']}\n")
