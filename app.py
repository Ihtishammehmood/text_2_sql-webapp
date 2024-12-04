import streamlit as st
import sqlite3
import google.generativeai as genai
from google.api_core import retry
import pandas as pd
import textwrap


# Load secrets for API key
api_key = st.secrets["GOOGLE_API_KEY"]

# Setup Generative AI Model
genai.configure(api_key=api_key)

# Connect to the Chinook database
db_file = "assets/Chinook.db"
db_conn = sqlite3.connect(db_file)

# Define database interaction functions
def list_tables() -> list[str]:
    """Retrieve the names of all tables in the database."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [t[0] for t in cursor.fetchall()]

def describe_table(table_name: str) -> list[tuple[str, str]]:
    """Retrieve the schema of a given table."""
    cursor = db_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    return [(col[1], col[2]) for col in schema]

def execute_query(sql: str) -> list[list[str]]:
    """Execute a SELECT query and return results."""
    cursor = db_conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

# Register database tools
db_tools = [list_tables, describe_table, execute_query]

# Configure the Generative AI model with tools
model = genai.GenerativeModel(
    "models/gemini-1.5-flash-latest",
    tools=db_tools,
    system_instruction="""You are a helpful chatbot that can interact with an SQL database. You will take the users questions and turn them into SQL queries using the tools
available. Once you have the information you need, you will answer the user's question using
the data returned. Use list_tables to see what tables are present, describe_table to understand
the schema, and execute_query to issue an SQL SELECT query.Retrieve the result in tabular format."""
)

# Streamlit UI
st.title("Text-to-SQL")

# Start chat session
chat = model.start_chat(enable_automatic_function_calling=True)

# Sample questions
sample_questions = [
    "What are the names of all the tables in the database?",
    "List all the albums by the artist 'AC/DC'.",
    "How many tracks are there in the 'Rock' genre?",
    "Which artist has the most albums?",
    "Which tracks are part of the album ,Let There Be Rock?",
    "List the names of customers who have purchased more than 10 tracks.",
    "Which employees have sold the most albums?"
    "Count the number of tracks are there in each genre",
    "Which country has the most customers?",
    "Which sales agent has the highest total sales amount?",
]

# Sidebar for sample questions
st.sidebar.title("Sample Questions")
selected_question = st.sidebar.selectbox("Choose a question:", sample_questions)

# User interaction
query = st.text_input("Or ask your own question about the database:", value=selected_question)

if st.button("Submit Query"):
    if query.strip():
        try:
            with st.spinner("Thinking..."):
                # Send user query to Generative AI
                retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
                response = chat.send_message(query, request_options=retry_policy)

            # Display the chat response
            st.subheader("Response:")
            st.write(response.text)

            # Display executed SQL if available
            st.subheader("Executed SQL (if any):")
            for event in chat.history:
                for part in event.parts:
                    if fn := part.function_call:
                        sql_query = fn.args.get("sql", None)
                        if sql_query:
                            st.code(sql_query)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query!")

# Explore the database schema
if st.checkbox("Show database schema"):
    tables = list_tables()
    for table in tables:
        st.write(f"**{table}**")
        schema = describe_table(table)
        schema_df = pd.DataFrame(schema, columns=["Column", "Type"])
        st.dataframe(schema_df)
        
        
# # Function to display chat history
# def display_chat_history(chat):
#     st.subheader("Chat History")
#     for event in chat.history:
#         st.markdown(f"**{event.role.capitalize()}:**")
#         for part in event.parts:
#             if txt := part.text:
#                 st.markdown(f"> {txt}")
#             elif fn := part.function_call:
#                 args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
#                 st.markdown(f"**Function call:** `{fn.name}({args})`")
#             elif resp := part.function_response:
#                 st.markdown("**Function response:**")
#                 st.markdown(f"> {textwrap.indent(str(resp), '    ')}")

# # Display chat history
# display_chat_history(chat)