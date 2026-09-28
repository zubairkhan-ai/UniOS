from .question_rewriter import rewrite_question


history = [
    {
        "type": "rag",
        "user": "What is TCP?",
        "ai": "TCP is a transport layer protocol."
    }
]


tests = [
    "What are its advantages?",
    "What are its disadvantages?",
    "How does it work?",
    "Why is it important?",
    "What is TCP?"
]


for question in tests:

    rewritten = rewrite_question(question, history)

    print("--------------------------------")
    print("Original :", question)
    print("Rewritten:", rewritten)