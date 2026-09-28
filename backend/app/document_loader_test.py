from pathlib import Path

from document_loader import load_powerpoint


PROJECT_ROOT = Path(__file__).resolve().parents[2]

file_path = (
    PROJECT_ROOT
    / "data"
    / "lectures"
    / "DAA"
    / "Week01"
    / "Week 1-Lecture 3.pptx"
)


documents = load_powerpoint(file_path)


print("\n===================================")
print("DOCUMENT METADATA TEST")
print("===================================")

print("Documents loaded:", len(documents))


for document in documents:

    print("\n-----------------------------------")

    print("Course:")
    print(document.metadata["course"])

    print("Week:")
    print(document.metadata["week"])

    print("Source:")
    print(document.metadata["source"])

    print("Slide:")
    print(document.metadata["slide"])