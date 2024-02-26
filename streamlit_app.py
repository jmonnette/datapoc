import streamlit as st
import redirect
import retrieve_github as rg
import langchain_helper as lh

st.set_page_config(layout="wide")
USER_NAME = "jmonnette"

def change_db():
    print("Changing DB")

repos = rg.get_repos(USER_NAME)
repo_dict = {}
for repo in repos:
     repo_dict[repo["full_name"]] = repo

repo = st.sidebar.selectbox("Repo", repo_dict.keys(), on_change=change_db)
if repo:
    repo_name = repo_dict[repo]["name"]
    options = {}
    
    tags = rg.get_tags(USER_NAME, repo_name)
    branches = rg.get_branches(USER_NAME, repo_name)

    for tag in tags:
        options[f"{tag['name']} (Tag)"] = tag
    for branch in branches:
        options[f"{branch['name']} (Branch)"] = branch

    sorted_options = list(options.keys())
    sorted_options.sort()

    tag1 = st.sidebar.selectbox("Tag 1", sorted_options)
    # Create a text input widget in sidebar
    input_text = st.sidebar.text_area(label="Prompt", height=10)

    compare_enabled = st.sidebar.toggle("Compare Versions", False)
    
    tag2 = st.sidebar.selectbox("Tag 2", sorted_options, disabled=not compare_enabled)
    cache_enabled = st.sidebar.toggle("Enable Content Cache", True)
    search_enabled = st.sidebar.toggle("Enable Search Index", True)
    memory_enabled = st.sidebar.toggle("Enable Agent Memory", True)

# Create a button in sidebar
if st.sidebar.button('Press me'):
        prompt = f"{input_text}"
        if compare_enabled:
             prompt = prompt + f"\nCompare version {options[tag1]['commit'].sha} to version {options[tag2]['commit'].sha}"

        with st.expander(label="Results", expanded=True):
            input = st.empty()
            messages = st.empty()
            result = st.empty()

        with st.expander(label="Console", expanded=False):
            console = st.empty()

        input.markdown(f"**Agent input**:  \n*{prompt}*")
    
        with redirect.stdout(to=console):
            key = f"{repo_dict[repo]['owner']}/{repo_dict[repo]['name']}/{options[tag1]['name']}"
            cache = {}
            if "repo_content_cache" in st.session_state:
                cache = st.session_state.repo_content_cache
            if cache_enabled and key not in cache:
                messages.markdown("**Status:** Building cache")
                rg.build_repo_content_cache(cache, repo_dict[repo]["owner"],  repo_dict[repo]["name"], tag_name=options[tag1]['name'])
                st.session_state.repo_content_cache = cache
                rg.set_repo_content_cache(st.session_state.repo_content_cache)

            search_dbs = {}
            if "search_dbs" in st.session_state:
                 search_dbs = st.session_state.search_dbs
            if search_enabled and key not in search_dbs:
                 messages.markdown("**Status:** Building search index")
                 search_dbs[key] = lh.create_db(repo_dict[repo]["owner"], repo_dict[repo]["name"], tag_name=options[tag1]['name'])
            st.session_state.search_dbs = search_dbs

            messages.markdown("**Status:** Running agent")
            search_db = search_dbs[key] if key in search_dbs and search_enabled else None
            memory = st.session_state.agent_memory if "agent_memory" in st.session_state and memory_enabled else None
            agent_output = lh.run_agent(search_db, memory, prompt, repo_dict[repo]["owner"], repo_dict[repo]["name"], tag_name=options[tag1]['name'])
            st.session_state.agent_memory = agent_output["memory"]
            result.empty().write(agent_output["result"])
            messages.markdown("**Status:** Complete")
else:
    st.write('Waiting for you to type something and click the button...')