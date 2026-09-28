from retriever import retrieve_documents
from answer_extractor import extract_definition


questions = [
    "What is time complexity?",
    "What is complexity?"
]


for question in questions:

    print("\n===================================")
    print("QUESTION:", question)
    print("===================================")

    documents = retrieve_documents(question)

    if not documents:

        print("No relevant documents found.")
        continue

    answer = extract_definition(
        question,
        documents
    )

    print("\nExtracted answer:")
    print(answer)