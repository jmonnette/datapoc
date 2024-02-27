# Langchain SQL PoC

This is a Python script that interacts with a SQLite database, processes user queries and retrieves corresponding results. It uses the OpenAI GPT model for generating SQL queries based on natural language input, specifically GPT-4.

The script does the following

1. Retrieves a list of tables, descriptions, and referenced tables from the database
2. Passes this list to an LLM to decide which tables should be included in the query
3. Retrieves the DDL for the selected tables
4. Generates an SQL query based on the DDL

## Current Limitations

1. Only works with SQLite
2. Requires a TableMetadata table to store additional metadata about tables (i.e., descriptions and referenced tables

## Requirements

1. Python3
2. Python packages: langchain_community.utilities, dotenv, ast, json, typing, langchain_openai, langchain.callbacks.tracers, langchain.output_parsers, langchain.prompts, operator, langchain.chains, langchain_core.runnables. 

## How it works

1. The script first loads environment variables using the `dotenv` package.
   
2. It defines three classes, `Table`, `Tables`, and `get_table_chain`. 
- Table and Tables are Pydantic Base models used for data validation and settings management using Python type annotations.
- `get_table_chain` function creates a langchain where it fetches all the SQL tables that might be relevant to a user's question and further includes the selected tables and the referenced tables.
   
3. It queries a SQLite database 'Chinook.db', gets metadata about the database tables, and generates a list of table names.

4. It creates a langchain for generating SQL queries using AzureChatOpenAI (GPT-4) and the database, and another langchain for getting tables related to the user's questions. It then combines these langchains into a complete full_chain.

5. Finally, the script invokes the full_chain with a user's query and prints the results obtained from the SQL query executed on the database.

Note: This script specifically answers questions about artists' sales and songs from a music database based on the user's queries. However, it can be adapted to work with other domains by modifying the SQL queries and table names.

## How to Run

1. Clone the repository.
2. Install all dependencies by running pip install for each package listed in requirements.
3. Set the necessary environment variables (if any).
4. Run `python script.py` in your terminal.

## Caution
Ensure you have the `Chinook.db` SQLite database file in your working directory before running the script. The DATABASE_URL should be valid and database should contain the correct records otherwise it may produce incorrect or empty results. 

## Dependencies

The functioning of this script depends on the OpenAI GPT model and the langchain library for chained runnables. In addition, the script relies on the SQLite database to generate the required results.