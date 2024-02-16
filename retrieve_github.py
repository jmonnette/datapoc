import os
import base64
import sys
from github import Github
from dotenv import load_dotenv

# Read environment variable using dotenv
load_dotenv()
github_token = os.getenv('GITHUB_TOKEN')

def save_release_files(user_name, repo_name, release_tags):
    github_instance = Github(github_token)
    repo = github_instance.get_user(user_name).get_repo(repo_name)

    for release_tag in release_tags:
        releases = repo.get_tags()
        for release in releases:
            if release.name == release_tag:
                # Create directory for release tag if it doesn't exist
                dir_name = f'code/{release_tag}'
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)

                # Get commit of release
                commit = release.commit
                tree = repo.get_git_tree(sha = commit.sha, recursive=True)

                # Iterate over all directories/files in the release
                for entry in tree.tree:
                    file_content = repo.get_contents(entry.path, ref=release_tag)

                    if file_content.type == "file":
                        # Write the file to directory with tag name inserted between file name and extension
                        filename, file_extension = os.path.splitext(file_content.name)
                        new_filename = f"{filename}_{release_tag}{file_extension}"
                        with open(f'{dir_name}/{new_filename}', 'w') as new_file:
                            new_file.write(file_content.decoded_content.decode())

if __name__ == "__main__":
    # get parameters from command line arguments
    username = sys.argv[1]
    repo = sys.argv[2]
    tags = [tag for tag in sys.argv[3:]]

    # Call the function with command line arguments
    save_release_files(username, repo, tags)
