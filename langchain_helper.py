from langchain.document_loaders.text import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain_openai import AzureChatOpenAI, AzureOpenAI, AzureOpenAIEmbeddings
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
from langchain import hub
#from langchain.schema import HumanMessage
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.agents import AgentExecutor,create_react_agent
#from langchain.agents import AgentType
from langchain_core.prompts import PromptTemplate
from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory

import fnmatch
import json
from dotenv import load_dotenv

import diff_github as dg
import retrieve_github as rg



load_dotenv()

#TODO: Need to make this a class so that we don't have to use global variables
def create_db(user_name, repo_name, tag_name="main") -> FAISS:
    global _user_name
    global _repo_name
    global _tag_name
    global _db
    _user_name = user_name
    _repo_name = repo_name
    _tag_name = tag_name

    print(f"Building FAISS database for {user_name}/{repo_name}/{tag_name}")
    embeddings = AzureOpenAIEmbeddings(azure_deployment='text-embedding-ada-002')
    db = None

    for file in rg.get_file_list(user_name, repo_name, tag_name):
        print(f"Loading file {file}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_text(get_file_content(file))
        metadata = [{"source_file": file}] * len(texts)
        if db is None:
            db = FAISS.from_texts(texts, embeddings, metadata)
        else:
            db.add_texts(texts, metadata)
    print("FAISS database complete")
    return db


def get_response_from_query(db):
    """
    text-davinci-003 can handle up to 4097 tokens. Setting the chunksize to 1000 and k to 4 maximizes
    the number of tokens to analyze.
    """

    query = "What does get_credit_score do?"
    docs = db.similarity_search(query, k=4)
    docs_page_content = " ".join([d.page_content for d in docs])

    llm = AzureChatOpenAI(azure_deployment="gpt-35-turbo")
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
            Answer the following question: {question}
            By searching the following code file: {docs}
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.invoke({"question":query, "docs":docs_page_content})
    return response

@tool
def search_codebase(query):
    """
        Search the codebase for relevant content based on the given query
    """
    print(f"Searching with query {query}")
    docs = _db.similarity_search(query, k=4)
    return "\n".join([f"Source File Name: {d.metadata['source_file']}\n{d.page_content}" for d in docs])

@tool
def get_file_tree(filter='{"filter":"*"}'):
    """
    Retrieves the list of files from the program that match a specified wildcard filter. 
    If no filter is supplied, all files are returned.
    
    This function uses the specified wildcard filter (using Unix shell-style wildcards) to return a 
    list of filenames.

    Args:
        file_filter (str, optional): A string representing the Unix shell-style wildcard filter.
                                     Common wildcards include '*' (matches everything), 
                                     '?' (matches single characters), and '[seq]' (matches any 
                                     character in seq). Defaults to '*' if not supplied.

    Returns:
        list: A list of filenames (strings) in the program that match the provided filter. 
              If no matches are found, an empty list is returned.

    Example:
        >>> file_list = get_file_list('*.py')
        >>> print(file_list)
        ['file1.py', 'file2.py', 'file3.py']

        >>> all_files = get_file_list()
        >>> print(all_files)
        ['file1.py', 'file2.py', 'file3.py', 'file4.txt']

    Note:
        In a Unix shell-style wildcard, '*' matches everything (including the dot in a filename), 
        '?' matches any single character, and '[seq]' matches any character in seq.
    """

    isjson, filter_dict = is_json_object(filter)
    file_filter = "*"
    if isjson and  "filter" in filter_dict:
        file_filter = filter_dict["filter"]
        
    file_list = rg.get_file_tree(_user_name, _repo_name, _tag_name)
    if file_filter == "*":
        return file_list
    
    return [path for path in file_list if fnmatch.fnmatch(path, file_filter)]

"""     files = glob.glob()
    print(f"Getting files: {files}")
    if len(files) > 0:
        return files
    else:
        return glob.glob("*") """
@tool
def get_commit_messages(tags):
    """
        Retrieve the commit messages between two versions of the program

        Args:
        tags (dict): The two tags to compare formatted as a dictionary with keys "tag1" and "tag2"

    Returns:
        str: The commit messages as a single string.
    """

    tags = json.loads(tags)
    return "\n".join(message for message in rg.get_commit_messages("jmonnette", "datapoc", tags["tag1"], tags["tag2"]))

#TODO: Not sure if this is useful or not
# @tool
# def get_multiple_file_content(file_list=""):
#     """
#         Retrieves the content of multiple files at once.  This can be much faster and more efficient
#         than getting the files one by one.

#         Args: A JSON array containing the list of files to include in the output.
#     """
#     return rg.get_all_files_content(_user_name, _repo_name, _tag_name)

@tool
def get_file_content(path):
    """
    Retrieves the content of a file at a specified path.

    This function opens a file located at the provided path, reads the content of the file, 
    and returns it as a string. Single quote characters in the path are removed before opening the file.

    Args:
        path (str): A string representing the path to the file. This should include the filename 
                     and its extension. Single quotes in the path are unnecessary and will be removed.

    Returns:
        str: The content of the file as a single string.

    Raises:
        FileNotFoundError: If the file does not exist at the provided path.
        IsADirectoryError: If the path is a directory.
        PermissionError: If the program does not have sufficient permission to read the file.

    Example:
        >>> file_content = get_file_content('example.txt')
        >>> print(file_content)
        'This is an example text file.'
    """

    file_path = ""
    isjson, path_dict = is_json_object(path)
    if isjson: 
        if "path" in path_dict:
            file_path = path_dict["path"]
    else:
        file_path = path.replace("'","")

    return rg.get_file_content(_user_name, _repo_name, file_path, _tag_name)
    
"""     with open(path.replace("'",""), 'r') as file:
        return file.read() """
    
@tool
def get_diffs(tags):
    """
        Retrieve the differences for all files between two versions of the program

        Args:
        tags (dict): The two tags to compare formatted as a dictionary with keys "tag1" and "tag2"

    Returns:
        str: The differences as a single string.
    """

    tags = json.loads(tags)
    return "\n".join([f"Filename: {diff['filename']}\nPatch: {diff['patch']}" for diff in dg.diff_shas(tags["tag1"], tags["tag2"], "jmonnette", "datapoc")])

#TODO: Turn this into a class to eliminate need for global variables
_user_name = ""
_repo_name = ""
_tag_name = ""
_db = None

def run_agent(db, user_prompt, user_name, repo_name, tag_name="main"):
    global _user_name
    global _repo_name
    global _tag_name
    global _db
    _user_name = user_name
    _repo_name = repo_name
    _tag_name = tag_name
    _db = db

    prompt = hub.pull("hwchase17/react")

    llm = AzureChatOpenAI(azure_deployment="gpt-4", temperature=0)
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    tools = [get_file_tree, get_file_content, get_diffs, get_commit_messages, wikipedia]
    if db is not None:
        tools.append(search_codebase)
    agent = create_react_agent(
        tools=tools,
        llm=llm,
        prompt=prompt)
    #TODO: Add memory to allow conversations.  Needs to be cached.
    #memory = ConversationBufferMemory()
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    return agent_executor.invoke(
        {"input": user_prompt})

def is_json_object(myjson):
    json_object = None
    if "{" in myjson:
        try:
            json_object = json.loads(myjson)
        except ValueError:
            stripped_json = myjson.replace("'","\"")
            if stripped_json == myjson:
                return False, json_object
            return is_json_object(stripped_json)
        return True, json_object
    return False, json_object

if __name__ == "__main__":
    #print(get_response_from_query(create_db()))
    #print(run_agent())
    #print(get_file_list('*'))
    #print(get_file_content('diff.py'))

    # print(is_json_object("'readme.md'"))
    # print(is_json_object('"readme.md"'))
    # print(is_json_object("{'path':'readme.md'}"))
    # print(is_json_object('{"path":"readme.md"}'))

    cache = {}
    rg.build_repo_content_cache(cache, "jmonnette", "datapoc")
    rg.set_repo_content_cache(cache)
    create_db("jmonnette", "datapoc")