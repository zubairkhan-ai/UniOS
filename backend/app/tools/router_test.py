from tool_router import route_request


print("\n================================")
print("TOOL ROUTER TEST")
print("================================")


questions = [
    "Add my CN assignment",
    "Add my RL homework",
    "Create a new KRR task",
    "What assignments are pending?",
    "Show all my assignments",
    "What assignments do I have?",
    "Mark assignment complete",
    "I finished my CN lab",
    "Delete my assignment",
    "Remove my homework",
    "What is CSS?"
]


for question in questions:

    intent = route_request(question)

    print("Result:", intent)

    print("--------------------------------")