# Github Helper Documentation

## retrieve_github.py
This Python script uses PyGithub, a Python library for interfacing with the Github API v3, to interact with Github to manage repositories. It fetches various details about repositories such as repo names, tags, branches, commit messages, and their file contents.

## Requirements
- Python >=3.6
- PyGithub
- python-dotenv
- fnmatch

## Environment Variables
The script uses the following environment variables:

- `GITHUB_TOKEN`: A Github personal access token to authenticate with the Github API. Make sure the token has appropriate permissions.

## How to Run
1. Clone the repository.
2. Install all dependencies by running `pip install -r requirements.txt`.
3. Set up your environment variables in a .env file.
4. Run `python script.py` within your terminal.

## How it works

- `get_repos`: Retrieves all repositories of a specific user.
- `get_tags`: Gets all the tags from a specific repository.
- `get_branches`: Retrieves all branches from a specific repository.
- `get_branches_and_tags`: Combines the results of `get_tags` and `get_branches`.
- `find_branch_or_tag`: Finds a branch or tag in a repository.
- `get_file_tree`: Retrieves the file tree from a repository.
- `get_file_list`: Returns a list of all files from a repository.
- `build_repo_content_cache`: Builds a cache for repository content.
- `get_file_content`: Retrieves file content from a repository.
- `get_commit_messages`: Retrieves commit messages from a repository between two specific commits.
- `save_release_files`: Saves files from certain release tags of a repository locally.

The main block of the script is currently commented out but it would have been used to get command-line arguments to perform desired actions.

## Features
This script can be useful to anyone wanting to automate management and extraction of data from Github repositories. It can be used to get repository branches, tags, commit messages, fetch file content, build a cache, and even save certain release files locally. It can also be used to get all commits between two specific points, a useful feature for managing version control in projects.

## Caution
Remember to store your Github token in an environment variable for security. Do not hardcode your tokens as it poses a serious security risk. Use python-dotenv to load environment variables from a .env file.

## diff_github.py

This script provides functionalities to interact with the GitHub API through the PyGitHub library. The functions contained in the script can be used to extract differences between two commits or tags in a given repository.

## Requirements
- Python >=3.6
- PyGitHub
- python-dotenv

## Environment Variables
The script uses the following environment variables:

1. `GITHUB_TOKEN`: Your GitHub access token to authenticate with the GitHub API.

## How to Run
1. Clone the repository.
2. Install all dependencies by running `pip install -r requirements.txt`, assuming all dependencies are listed in the `requirements.txt` file.
3. Set up your environment variables in a `.env` file.
4. Run `python script.py username repo_name tag1 tag2` within your terminal.

## How it works

1. The script first imports required modules and libraries, loads environment variables from `.env` and authenticates your token using GitHub.

2. `_diff_shas` is a private helper function that returns a generator consisting of dictionaries with filename and patch information for two given SHAs in a repository.

3. `diff_shas` is a function to get differences between two given SHAs in a repository.

4. `diff_commits` is a function to compare two commits from a repository, identified by their `sha` values.

5. `diff_tags` is a function to compare two tags from a repository, where tags are eventually converted to commit SHAs for comparison.

6. The main block of this script gets arguments from the command line and prints the differences using the `diff_tags` function.

## Features
This script can come handy while you want to access patches and file changes between two different versions of a program. It can be used to fetch differences of all files between two commits or tags.

## Caution
Remember that you need to provide your GitHub access token for this script to authenticate with GitHub API. It's preferred to store the GitHub access token in environment variables for security purposes. 

Also, ensure that you have the correct permissions to fetch differences on the desired repositories. 

## Dependencies
The PyGitHub library and the specified environment variables are fundamental for the functioning of this script.

Do remember to accommodate for the environment variables in .env file to be loaded before running your application that leverages the GitHub API.