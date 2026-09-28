from parameter_extractor import extract_assignment_parameters


print("\n================================")
print("PARAMETER EXTRACTOR TEST")
print("================================")


questions = [

    "Add my CN assignment due 2026-09-30",

    "Add my RL homework due September 28",

    "Create a KRR task due tomorrow",

    "Add COAL lab due in 5 days",

    "Add my CV assignment",

]


for question in questions:

    print("\nUser:")
    print(question)

    result = extract_assignment_parameters(
        question
    )

    print("\nExtracted:")

    print("Course:", result["course"])
    print("Title:", result["title"])
    print("Due Date:", result["due_date"])
    print("Description:", result["description"])

    print("--------------------------------")