from llm import generate_answer


context = """
Complexity is the number of steps required to solve a problem.

The time needed by an algorithm, expressed as a function
of the size of the problem it solves, is called the
time complexity of the algorithm T(n).
"""


question = "What is time complexity?"


print("\n===================================")
print("LLM TEST")
print("===================================")

print("\nQuestion:")
print(question)


answer = generate_answer(
    question,
    context
)


print("\nAnswer:")
print(answer)