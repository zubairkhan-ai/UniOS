from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from document_loader import load_powerpoint
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================================================
# 1. FIND PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# =========================================================
# 2. LECTURE PATH
# =========================================================

file_path = (
    PROJECT_ROOT
    / "data"
    / "lectures"
    / "DAA"
    / "Week01"
    / "Week 1-Lecture 3.pptx"
)


# =========================================================
# 3. LOAD LECTURE
# =========================================================

print("Loading lecture...")

documents = load_powerpoint(file_path)

print("Documents loaded:", len(documents))


# =========================================================
# 4. SPLIT INTO CHUNKS
# =========================================================

print("Creating chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print("Chunks created:", len(chunks))


# =========================================================
# 5. CHECK METADATA
# =========================================================

print("\n===================================")
print("METADATA CHECK")
print("===================================")

for chunk in chunks[:2]:

    print("\nCourse:", chunk.metadata["course"])
    print("Week:", chunk.metadata["week"])
    print("Source:", chunk.metadata["source"])
    print("Slide:", chunk.metadata["slide"])


# =========================================================
# 6. LOAD EMBEDDING MODEL
# =========================================================

print("\nLoading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# 7. CONNECT TO EXISTING CHROMA
# =========================================================

persist_directory = (
    PROJECT_ROOT / "data" / "chroma_db"
)

print("\nChecking existing Chroma collection...")

old_store = Chroma(
    persist_directory=str(persist_directory),
    collection_name="university_material",
    embedding_function=embeddings
)


# =========================================================
# 8. DELETE OLD COLLECTION
# =========================================================

print("Deleting old Chroma collection...")

old_store.delete_collection()

print("Old collection deleted.")


# =========================================================
# 9. CREATE FRESH CHROMA DATABASE
# =========================================================

print("\nCreating fresh Chroma database...")

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(persist_directory),
    collection_name="university_material"
)


# =========================================================
# 10. SUCCESS
# =========================================================

print("\n===================================")
print("VECTOR DATABASE CREATED")
print("===================================")

print("Stored chunks:", len(chunks))

print(
    "Database location:",
    persist_directory
)

print("\nMetadata stored:")

print("Course: DAA")
print("Week: Week01")
print("Slides: 1-10")