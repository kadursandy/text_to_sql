# 🧠 TEXT 2 SQL using LangGraph

A powerful and extensible **Text-to-SQL agent** powered by [LangGraph](https://docs.langgraph.dev) and LLMs. This project converts natural language questions into SQL queries and executes them on a target database. Useful for non-technical users to interact with databases using natural language.

## 🔧 Features

- 💬 Natural language to SQL translation using LLMs
- 🧠 Graph-based agent orchestration via LangGraph
- ⚙️ Tool calling for function-based database interactions
- 🗂️ Support for multiple SQL dialects (e.g., SQLite, PostgreSQL, Oracle)
- 🔌 Modular design for easy integration with your own schema and backend

## 📐 Architecture

- **LangGraph**: Controls the flow of the LLM-based agent
- **Function Calling Tools**: Used for schema inspection and SQL execution
- **LLM (OpenAI / Cohere )**: Generates SQL queries from natural language
- **Database Connector**: Executes the generated SQL on your database
- **Validation & Error Handling**: Handles bad queries or errors gracefully

## Install packages
```shell
pip install --upgrade --quiet langchain-community langgraph
pip install -qU "langchain[openai]"
pip install -qU "langchain[cohere]"
```

## Run
```shell
sqlite3 Chinook.db
.read Chinook_Sqlite.sql
create and add your api keys from https://dashboard.cohere.com/api-keys
python cohere_chat.py
```

## Output
```shell
{'write_query': {'query': 'SELECT COUNT(*) AS num_employees FROM Employee;'}}
{'execute_query': {'result': '[(8,)]'}}
{'generate_answer': {'answer': 'There are 8 employees.'}}
result=query='SELECT COUNT(DISTINCT ArtistId) AS count FROM Artist;', SELECT COUNT(DISTINCT ArtistId) AS count FROM Artist; <class '__main__.QueryOutputModel'>
{'write_query': {'query': 'SELECT COUNT(DISTINCT ArtistId) AS count FROM Artist;'}}
{'execute_query': {'result': '[(275,)]'}}
{'generate_answer': {'answer': 'There are 275 artists.'}}
```


