from pathlib import Path

from langchain_chroma import Chroma
from embeddings import get_embeddings


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHROMA_DIR = (
    PROJECT_ROOT
    / "data"
    / "chroma_db"
)

embeddings = get_embeddings()

vector_store = Chroma(
    persist_directory=str(CHROMA_DIR),
    collection_name="university_material",
    embedding_function=embeddings
)

results = vector_store._collection.get(
    where={
        "$and": [
            {"course": "web and ai"},
            {"week": "Week01"}
        ]
    },
    include=[
        "documents",
        "metadatas"
    ]
)

documents = results.get(
    "documents",
    []
)

metadatas = results.get(
    "metadatas",
    []
)

print("\n===================================")
print("WEB AND AI — WEEK01")
print("===================================")

print(
    "Documents found:",
    len(documents)
)

for index, (text, metadata) in enumerate(
    zip(documents, metadatas),
    start=1
):

    print("\n-----------------------------------")
    print("DOCUMENT:", index)
    print("-----------------------------------")

    print("Metadata:")

    for key, value in metadata.items():
        print(f"{key}: {value}")

    print("\nTEXT:")
    print(text[:1500])