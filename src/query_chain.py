from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

print("loading vector_db ....")

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = "chroma"

if db == "chroma":
    db = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
else:
    raise ValueError(f"Cannot recognize database - {db}")

print("quering question ....")
question = "What is HELIS?"
result = db.similarity_search(question, k=3)

print(result)

for i in range(len(result)):
    print(f"document {i}")
    print(result[i].page_content)
    print(f"\n")