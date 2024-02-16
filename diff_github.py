from github import Github
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

g = Github(os.getenv("GITHUB_TOKEN"))  # Get GitHub access token from environment variable

repo = g.get_repo("jmonnette/datapoc")  # replace with user and repository name

tags = repo.get_tags()
tag1 = "v0.0.3"  # replace with your tag1
tag2 = "v0.0.4"  # replace with your tag2

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
