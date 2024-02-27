import os
from github import Github
from dotenv import load_dotenv
import fnmatch

# Read environment variable using dotenv
load_dotenv()
github_token = os.getenv('GITHUB_TOKEN')
github_instance = Github(github_token)
repo_content_cache = {}

def get_repos(user_name):
    user = github_instance.get_user(user_name)
    repos = user.get_repos("owner")
    return ({"full_name": repo.full_name, "name": repo.name, "owner": repo.owner.login} for repo in repos)

def get_tags(user_name, repo_name):
    repo = github_instance.get_user(user_name).get_repo(repo_name)   

    return ({"name":tag.name, "commit": tag.commit} for tag in repo.get_tags())

def get_branches(user_name, repo_name):
    repo = github_instance.get_user(user_name).get_repo(repo_name)   

    return ({"name":branch.name, "commit": branch.commit} for branch in repo.get_branches())

def get_branches_and_tags(user_name, repo_name):
    yield from get_branches(user_name, repo_name)
    yield from get_tags(user_name, repo_name)

#TODO: What if a branch and a tag have the same name?
def find_branch_or_tag(user_name, repo_name, search_name):
    return next(ref for ref in get_branches_and_tags(user_name, repo_name) if ref["name"] == search_name)

def get_file_tree(user_name, repo_name, ref="main", filter="*"):
    repo = github_instance.get_user(user_name).get_repo(repo_name)   
    commit = find_branch_or_tag(user_name, repo_name, ref)["commit"]

    tree = repo.get_git_tree(sha=commit.sha, recursive=True).tree
    file_tree = {}

    for element in (element for element in tree if fnmatch.fnmatch(element.path, filter)):
        path_parts = element.path.split('/')
        current_level = file_tree

        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})

        if(element.type == "blob"):
            current_level[path_parts[-1]] = {"size": element.size}

    return file_tree

def get_file_list(user_name, repo_name, ref="main"):
    repo = github_instance.get_user(user_name).get_repo(repo_name)   

    commit = find_branch_or_tag(user_name, repo_name, ref)["commit"]

    tree = repo.get_git_tree(sha=commit.sha, recursive=True).tree
    file_list = []

    for element in tree:
        if(element.type == "blob"):
            file_list.append(element.path)

    return file_list

def build_repo_content_cache(cache, user_name, repo_name, tag_name="main"):
    repo_key = f"{user_name}/{repo_name}/{tag_name}"
    print(f"Priming content cache for {repo_key}")
    repo = github_instance.get_user(user_name).get_repo(repo_name)

    content_dict = {}
    cache[repo_key] = content_dict

    directories = [""]
    while directories:
        current_dir = directories.pop()
        content_list = repo.get_contents(current_dir, ref=tag_name)

        for content in content_list:
            try:
                if content.type == "dir":
                    directories.append(content.path)
                else:
                    content_dict[content.path] = content.decoded_content.decode()
            except Exception as e:
                print(f"Skipped {content.path} due to error: {e}")
    print("Content cache primed")

def set_repo_content_cache(cache):
    global repo_content_cache
    repo_content_cache = cache

#TODO: Needs to be made recursive... currently only looks at root folder
""" def get_all_files_content(user_name, repo_name, tag_name="main"):
    repo = github_instance.get_user(user_name).get_repo(repo_name)

    content_list = repo.get_contents("", ref=tag_name)
    all_content = ""
    for content in content_list:
        all_content = all_content + f"***** File name: {content.name}, Encoding: {content.encoding} *****\n{content.decoded_content.decode()}\n" 
    return all_content """


def get_file_content(user_name, repo_name, path, tag_name="main"):
    repo_key = f"{user_name}/{repo_name}/{tag_name}"
    repo = github_instance.get_user(user_name).get_repo(repo_name)

    if repo_key in repo_content_cache and path in repo_content_cache[repo_key]:
        print(f"Cache hit for {path}")
        return repo_content_cache[repo_key][path]
    else:
        print(f"Cache miss for {path}")
        return repo.get_contents(path, ref=tag_name).decoded_content.decode()
    
def get_commit_messages(user_name, repo_name, start_commit, end_commit):
    repo = github_instance.get_user(user_name).get_repo(repo_name)

    # Bound commits
    start_commit = repo.get_commit(start_commit)
    end_commit = repo.get_commit(end_commit)

    # Get datetime objects from bound commits
    start_date = start_commit.commit.committer.date
    end_date = end_commit.commit.committer.date

    # Return a generator to iterate over each commit in the repository
    return (commit.commit.message for commit in repo.get_commits(since=start_date, until=end_date))

def save_release_files(user_name, repo_name, release_tags):
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
    """ username = sys.argv[1]
    repo = sys.argv[2]
    tags = [tag for tag in sys.argv[3:]]
 """
    # Call the function with command line arguments
    #save_release_files(username, repo, tags)
    #print(get_file_content(username, repo, "generate_report.py"))
    #print([repo for repo in itertools.islice(get_repos("jmonnette"),5)])

    [print(x) for x in get_commit_messages("jmonnette", "datapoc","73a65dd75aac082d73de0d3160975303229b45e8", "50a40f0549e178f0de1624bb36c5d9dd4493ca96")]
