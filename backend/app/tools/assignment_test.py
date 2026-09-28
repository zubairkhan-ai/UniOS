from .assignment_tool import  (
    add_assignment,
    get_assignments,
    get_pending_assignments,
    complete_assignment,
    delete_assignment
)


print("\n================================")
print("ASSIGNMENT MANAGER TEST")
print("================================")


# --------------------------------
# 1. ADD ASSIGNMENT
# --------------------------------

result = add_assignment(
    course="CN",
    title="Computer Networks Lab 3",
    due_date="2026-09-25",
    description="Complete Packet Tracer topology."
)

print("\nADD:")
print(result)


# --------------------------------
# 2. ADD ANOTHER ASSIGNMENT
# --------------------------------

result = add_assignment(
    course="RL",
    title="Q-Learning Homework",
    due_date="2026-09-27",
    description="Implement Q-learning for Taxi environment."
)

print("\nADD:")
print(result)


# --------------------------------
# 3. GET ALL ASSIGNMENTS
# --------------------------------

print("\nALL ASSIGNMENTS:")

assignments = get_assignments()

for assignment in assignments:
    print(assignment)


# --------------------------------
# 4. GET PENDING ASSIGNMENTS
# --------------------------------

print("\nPENDING ASSIGNMENTS:")

pending = get_pending_assignments()

for assignment in pending:
    print(assignment)


# --------------------------------
# 5. COMPLETE FIRST ASSIGNMENT
# --------------------------------

if assignments:

    assignment_id = assignments[0]["id"]

    result = complete_assignment(assignment_id)

    print("\nCOMPLETE:")
    print(result)


# --------------------------------
# 6. SHOW UPDATED ASSIGNMENTS
# --------------------------------

print("\nUPDATED ASSIGNMENTS:")

assignments = get_assignments()

for assignment in assignments:
    print(assignment)


print("\n================================")
print("TEST COMPLETE")
print("================================")