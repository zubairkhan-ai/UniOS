from retriever import retrieve_documents


# =========================================================
# TEST 1
# =========================================================

question = "What is time complexity?"

documents = retrieve_documents(question)


print("\n===================================")
print("RETRIEVER TEST")
print("===================================")

print("\nQuestion:")
print(question)

print("\nRelevant documents:")

for document in documents:

    print(
        f"- Slide {document.metadata['slide']}"
    )


# =========================================================
# TEST 2
# =========================================================

question = "What is binary search?"

documents = retrieve_documents(question)


print("\n===================================")
print("SECOND TEST")
print("===================================")

print("\nQuestion:")
print(question)

print("\nRelevant documents:")

if documents:

    for document in documents:

        print(
            f"- Slide {document.metadata['slide']}"
        )

else:

    print(
        "No relevant lecture material found."
    )