from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Load the same embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Connect to existing Chroma database
vector_store = Chroma(
    persist_directory=str(
        PROJECT_ROOT / "data" / "chroma_db"
    ),
    collection_name="university_material",
    embedding_function=embeddings
)


# Question from student
question = "What is time complexity?"


# Search for relevant chunks
results = vector_store.similarity_search(
    question,
    k=3
)


print("\n===================================")
print("RETRIEVAL RESULTS")
print("===================================")

print("\nQuestion:")
print(question)


for i, document in enumerate(results, start=1):

    print("\n-----------------------------------")
    print(f"RESULT {i}")
    print("-----------------------------------")

    print("Source:", document.metadata["source"])
    print("Slide:", document.metadata["slide"])

    print("\nContent:")
    print(document.page_content)