from question_router import classify_question


questions = [
    "What is time complexity?",
    "Define insertion sort",
    "Explain time complexity",
    "Why do we analyze algorithms?",
    "Tell me about algorithms"
]


for question in questions:

    question_type = classify_question(question)

    print("-----------------------------------")
    print("Question:", question)
    print("Type:", question_type)