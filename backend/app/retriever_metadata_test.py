from retriever import retrieve_documents


# =========================================================
# TEST METADATA FILTERING
# =========================================================

question = "What is time complexity?"


print("\n===================================")
print("TESTING METADATA FILTERING")
print("===================================")


documents = retrieve_documents(
    question,
    course="DAA",
    week="Week01"
)


print("\n===================================")
print("RETRIEVED DOCUMENTS")
print("===================================")


if not documents:

    print("No relevant documents found.")

else:

    for document in documents:

        print("\nCourse:",
              document.metadata.get("course"))

        print("Week:",
              document.metadata.get("week"))

        print("Source:",
              document.metadata.get("source"))

        print("Slide:",
              document.metadata.get("slide"))

        print("Text:")
        print(document.page_content[:300])