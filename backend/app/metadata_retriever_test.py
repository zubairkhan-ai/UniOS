from retriever import retrieve_documents


# =========================================================
# TEST METADATA RETRIEVAL
# =========================================================

question = "What is time complexity?"

documents = retrieve_documents(question)


print("\n===================================")
print("METADATA RETRIEVAL TEST")
print("===================================")

print("\nQuestion:")
print(question)


print("\nRetrieved documents:")

if documents:

    for document in documents:

        print("\n-----------------------------------")

        print("Course:")
        print(document.metadata.get("course"))

        print("Week:")
        print(document.metadata.get("week"))

        print("Source:")
        print(document.metadata.get("source"))

        print("Slide:")
        print(document.metadata.get("slide"))

        print("\nText:")
        print(document.page_content)

else:

    print("No relevant documents found.")