from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import ast
import json
from typing import List, Optional, Dict

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter

from langchain.chains import create_sql_query_chain
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

class Table(BaseModel):
    """Table in SQL database."""

    name: str = Field(description="Name of table in SQL database.")
    description: str = Field(description="Description of table in SQL database.")
    referencedTables: Optional[str] = Field(description="Comma separated list of tables that this table references.")

class Tables(BaseModel):
    tables: List[Table]

def get_table_chain(llm):

    tablesPromptString = """Return ALL the SQL tables that MIGHT be relevant to the user question.
    The tables are:

    {tables}

    Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed.

    Format the output as a JSON array.

    {query}
    """

    referencedPromptString = """Create a list that includes ALL the selected tables AND ALL tables that the selected tables reference.
    The selected tables are:

    {selected_tables}

    The full list of tables is:

    {tables}

    {format_instructions}
    """

    parser = PydanticOutputParser(pydantic_object=Tables)

    chain = (
        PromptTemplate.from_template(tablesPromptString)
        | llm
        | {"selected_tables": RunnablePassthrough(),
            "tables": RunnablePassthrough(),
            "format_instructions": lambda x : parser.get_format_instructions()}
        | PromptTemplate.from_template(referencedPromptString)
        | llm
        | parser
        ).with_types(input_type=Dict[str, str], output_type=Tables)

    
    return chain

def get_table_names(all_selected_tables):
    return [table.name for table in all_selected_tables.tables]

db = SQLDatabase.from_uri("sqlite:///Chinook.db")
llm = AzureChatOpenAI(azure_deployment="gpt-4", temperature=0)
table_names = [{'name': table[0], 'description': table[1], 'referencedTables': table[2]} for table in ast.literal_eval(db.run("SELECT * FROM TableMetadata"))]

query_chain = create_sql_query_chain(llm, db)
table_chain = ({"query": itemgetter("question"), "tables": itemgetter("tables")} 
        | get_table_chain(llm) 
        | get_table_names)
full_chain = RunnablePassthrough.assign(table_names_to_use=table_chain) | query_chain


"""
Questions: 

What genres are the Alanis Morisette songs?
Which artist has the most songs?
Which artist has the most sales?
Which artist has the most sales in dollars?
Which artist had the highest month over month sales growth of all time?

"""
sql_query = full_chain.invoke({
    "question": """Looking at the total invoiced dollar amount (invoice quantity * unit price) per month for each artist 
                    and comparing to the previous month for that artist, 
                    which artist had the highest month over month sales growth of all time?
                    Include the artist name, month, month sales, previous month sales, and percent growth in the output.
                    """, "tables": json.dumps(table_names)}
                    
                    # Uncomment the line below to get verbose logging of the chain
                    ) #    , config={'callbacks': [ConsoleCallbackHandler()]})

print(sql_query)
sql_result = db.run(sql_query)
print(sql_result)