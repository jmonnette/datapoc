from github import Github
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Get parameters from command line
repo_username = sys.argv[1]
repo_name     = sys.argv[2]
tag1          = sys.argv[3]
tag2          = sys.argv[4]

g = Github(os.getenv("GITHUB_TOKEN"))  # Get GitHub access token from environment variable

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
    compare = repo.compare(sha1, sha2)
    for file in compare.files:
        print(f"Filename : {file.filename}\nPatch : {file.patch}\n")
