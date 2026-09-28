# ============================================
# ASSIGNMENT TOOL-CALLING AGENT
# ============================================

from assignment_tool import (
    add_assignment_tool,
    get_assignments_tool,
    get_pending_assignments_tool,
    complete_assignment_tool,
    delete_assignment_tool,
)


# --------------------------------------------
# LOAD TOOLS
# --------------------------------------------

tools = [
    add_assignment_tool,
    get_assignments_tool,
    get_pending_assignments_tool,
    complete_assignment_tool,
    delete_assignment_tool,
]


# --------------------------------------------
# SHOW AVAILABLE TOOLS
# --------------------------------------------

print("\n================================")
print("ASSIGNMENT AGENT")
print("================================")

print("\nAvailable tools:")

for tool in tools:
    print(f"- {tool.name}")


# --------------------------------------------
# TEST A TOOL DIRECTLY
# --------------------------------------------

print("\n================================")
print("DIRECT TOOL TEST")
print("================================")

result = add_assignment_tool.invoke({
    "course": "KRR",
    "title": "Knowledge Graph Homework",
    "due_date": "2026-09-29",
    "description": "Build a small knowledge graph."
})

print("\nResult:")
print(result)


# --------------------------------------------
# GET ASSIGNMENTS
# --------------------------------------------

print("\n================================")
print("CURRENT ASSIGNMENTS")
print("================================")

result = get_assignments_tool.invoke({})

for assignment in result:
    print(assignment)


print("\n================================")
print("TEST COMPLETE")
print("================================")