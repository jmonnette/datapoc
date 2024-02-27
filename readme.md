# Data PoC
The purpose of this project is to investigate and prove out the usefulness of LLMs in analyzing data differences and identifying the causes of these differences in underlying code.  There are three sub-PoCs in this project:

1. Report Compare (folder: report_compare)
2. SQL Query Generation (folder: sql_poc)
3. GitHub Code Analysis (folder: .)

# GitHub Code Analysis Streamlit+Langchain App

This application uses Streamlit for the UI and Langchain for the backend.  The Langchain code creates an LLM driven agent that, for a selected GitHub repo, can retrieve code, search the code for the most relevant info, fetch commit comments, and compare different versions.  The agent uses the LLM to reason about which actions to take based on a prompt, select an available tool to take the action, pass parameter values to the selected tool, and reason about next steps based on the information retrieved by the action.

The application has options to enable content caching, search indexing, and agent memory.

## Setup

Before you run the app, you need to set up your environment. Make sure to have your GitHub username set in an environment variable called `GITHUB_USER_NAME`. You can use an `.env` file for this.

## How to run the application

```bash
streamlit run streamlit_app.py
```

## Application interface

In the sidebar:

1. Choose a **repository**. For the chosen repository, the dropdown is automatically populated with the names of the different branches and tags present in that repo.

2. Choose a **Tag** you want to use. 

3. Input a **prompt** text.

4. Choose to compare versions with a toggle button. If enabled, another tag can be selected for comparison.

5. Option to **enable Content Cache**.

6. Option to **enable Search Index**.

7. Option to **enable Agent Memory**.

You can then press the 'Press me' button. Depending on your settings, results and console outputs will be displayed on the screen.

The application handles stdout redirect to show console outputs using the `redirect` module, and it also interacts with GitHub's repository content and builds a cache of it for quick retrieval.

Should any error occurs during runtime, appropriate error logs will be displayed.

## Dependencies

The main dependencies of the app are:

- streamlit
- redirect
- github_helper.retrieve_github
- langchain_helper
- python-dotenv
- os

You should install these modules via `pip` to ensure smooth running of the application.

# Langchain Helper

This script provides functionalities to interact with the GitHub API to retrieve files and status of repositories and provides facilities for language modeling, text comparison and more.

## Requirements
- Python >=3.6
- langchain.text_splitter
- langchain.vectorstores.faiss
- langchain_openai
- langchain.prompts
- langchain.chains
- langchain 
- langchain.tools
- langchain.tools.WikipediaQueryRun
- langchain.agents
- langchain_community.utilities.WikipediaAPIWrapper
- langchain.memory.ConversationBufferMemory
- github_helper.diff_github
- github_helper.retrieve_github
- python-dotenv
- fnmatch
- json

## How it works

1. The `create_db` function initializes an FAISS (Facebook's AI Similarity Search) database, which is a library for efficient similarity search. This function asks for user's github username, repo name and a tag name. 

2. The `get_response_from_query` function interacts with the database and returns responses from the database.

3. The `search_codebase` function, decorated as a @tool (a langchain tool), is used for searching within the codebase.

4. The `get_file_tree` function, decorated as a @tool, retrieves the list of files from the program that match a specified wildcard filter. If no filter is supplied, it retrieves all files.

5. The `get_commit_messages` function, decorated as a @tool, fetches commit messages from the github API.

6. The `get_diffs` function, decorated as a @tool, fetches differences of all files between two versions of the program.

7. The `run_agent` function runs an agent that makes use of the earlier mentioned functionality to operate on language models.

8. `get_file_content`, another tool, fetches the content of the mentioned file.

Note : The *AgentExecutor* is constructed with a collection of tools and langchain model. When invoked, it adds the tools to its memory and then executes the script's functions sequentially. 

This script also includes ability to recognize whether an entered string is JSON or not, using the `is_json_object` function. 

Do remember to accommodate for environment variables in .env file to be loaded before running your application that leverages github API. 

## Features
This script can be used as a modular set of tools for various language modeling, text comparison tasks and also interacting with the Github API to retrieve file statuses and more.
