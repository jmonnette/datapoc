import os
import base64
from github import Github

def save_release_files(github_token, user_name, repo_name, release_tag):
    github_instance = Github(github_token)
    repo = github_instance.get_user(user_name).get_repo(repo_name)
    releases = repo.get_releases()
    for release in releases:
        if release.tag_name == release_tag:
            # Create directory for release tag if it doesn't exist
            if not os.path.exists(release_tag):
                os.makedirs(release_tag)

            # Get commit of release
            commit = release.commit
            tree = repo.get_git_tree(sha = commit.sha, recursive='1')

            # Iterate over all directories/files in the release
            for entry in tree.tree:
                file_content = repo.get_contents(entry.path, ref=release_tag)

                if file_content.type == "file":
                    # Save each file in new directory named after the release tag
                    with open('data/' + release_tag + '/' + file_content.name, 'w') as new_file:
                        new_file.write(file_content.decoded_content.decode())

if __name__ == "__main__":
    save_release_files("<ACCESS_TOKEN>", "<USER_NAME>", "<REPO_NAME>", "<RELEASE_TAG>")
