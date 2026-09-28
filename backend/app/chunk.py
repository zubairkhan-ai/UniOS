from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from document_loader import load_powerpoint


# --------------------------------
# 1. Find project root
# --------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------
# 2. Lecture path
# --------------------------------

file_path = (
    PROJECT_ROOT
    / "data"
    / "lectures"
    / "Week 1-Lecture 3.pptx"
)


# --------------------------------
# 3. Load lecture
# --------------------------------

documents = load_powerpoint(file_path)

print("Original documents:", len(documents))


# --------------------------------
# 4. Create text splitter
# --------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


# --------------------------------
# 5. Split documents
# --------------------------------

chunks = splitter.split_documents(documents)


# --------------------------------
# 6. Display results
# --------------------------------

print("Total chunks:", len(chunks))


for i, chunk in enumerate(chunks):

    print("\n================================")
    print("CHUNK", i + 1)
    print("================================")

    print("Source:", chunk.metadata["source"])
    print("Slide:", chunk.metadata["slide"])

    print("\nText:")
    print(chunk.page_content)