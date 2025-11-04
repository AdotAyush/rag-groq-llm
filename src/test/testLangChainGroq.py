from langchain_groq import ChatGroq
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv 

print("API KEY:", os.getenv("GROQ_API_KEY"))
print("Current working directory:", os.getcwd())
load_dotenv()


llm = ChatGroq(model="groq/compound", api_key=os.getenv("GROQ_API_KEY"))
print("*****************")
print(llm.invoke("Explain RAG in brief to me").content)