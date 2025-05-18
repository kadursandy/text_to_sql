from langchain_community.chat_models import ChatOCIGenAI
import getpass
import os
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from pydantic import BaseModel, Field
import pdb
import logging
logging.basicConfig()
logging.getLogger("oci").setLevel(logging.DEBUG)


class QueryOutputModel(BaseModel):
    """Tool to generate a SQL query from a natural language question."""

    query: str = Field(..., description="Syntactically valid SQL query to execute on the database.")

    class Config:
        title = "QueryOutputModel"
        description = "Tool that returns a SQL query to retrieve the answer to the user's question."


db = SQLDatabase.from_uri("sqlite:///Chinook.db")
print(f"dialect={db.dialect}")
print(f"get_usable_table_names={db.get_usable_table_names()}")
db.run("SELECT * FROM Artist LIMIT 10;")


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str


config_profile = "DEFAULT"
compartment_id = "<compartment_ocid_or_tenancy_ocid>"
model_id = "ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyanrlpnq5ybfu5hnzarg7jomak3q6kyhkzjsl4qj24fyoq"
service_endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
provider = "cohere"


llm = ChatOCIGenAI(
    model_id=model_id,
    service_endpoint=service_endpoint,
    compartment_id=compartment_id,
    auth_type="API_KEY",
    auth_profile=config_profile,
    provider=provider,
    model_kwargs={"temperature": 0, "top_p": 0.75, "max_tokens": 500}
)

# llm = init_chat_model("command-r-plus", model_provider="cohere")

# response = llm.invoke("Tell me one fact about earth", temperature=0.7)
# print(response)

system_message = """
Given an input question, create a syntactically correct {dialect} query to
run to help find the answer. Unless the user specifies in his question a
specific number of examples they wish to obtain, always limit your query to
at most {top_k} results. You can order the results by a relevant column to
return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the
few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema
description. Be careful to not query for columns that do not exist. Also,
pay attention to which column is in which table.

Only use the following tables:
{table_info}
"""

user_prompt = "Question: {input}"

query_prompt_template = ChatPromptTemplate(
    [("system", system_message), ("user", user_prompt)]
)

# for message in query_prompt_template.messages:
#     message.pretty_print()


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information."""
    # pdb.set_trace()
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutputModel)
    result = structured_llm.invoke(prompt)
    print(f"result={result}, {result.query} {type(result)}")
    return {"query": result.query}


def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}


def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}


if __name__ == '__main__':
    # write_query({"question": "How many Employees are there?"})
    # print(f"res={response}")
    graph_builder = StateGraph(State).add_sequence(
        [write_query, execute_query, generate_answer]
    )
    graph_builder.add_edge(START, "write_query")
    graph = graph_builder.compile()

    for step in graph.stream(
            {"question": "How many employees are there?"}, stream_mode="updates"
    ):
        print(step)

    for step in graph.stream(
            {"question": "How many artists are there?"}, stream_mode="updates"
    ):
        print(step)
