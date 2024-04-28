from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import json

db = "chroma"
chunk_size = 512
chunk_overlap = 30

# Chunking the data
def get_dataset():
    with open('stockDataset.json', 'rb') as file:
        docs = json.load(file)
    return docs


def get_chunks(size, overlap):
    docs = get_dataset()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = []
    for data in docs:
        subset = text_splitter.create_documents([data["abstract"]])
        for chunk in subset:
            chunk.metadata={"doc_id": data["index"], "title": data["title"]}
        chunks += subset
    
    print(chunks[0])
    return chunks

## vector db creation
chunks = get_chunks(chunk_size, chunk_overlap)
print(f"number of chunks {len(chunks)}")


def save_vector_db(db):
    if db == "chroma":
        print("creating chroma db ....")
        persist_directory = 'chroma_db/'
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            persist_directory=persist_directory
        )
    else:
        raise ValueError(f"Cannot identify database - {db}")

    print(f"Successfully saved embeddings in {db}")

save_vector_db(db)