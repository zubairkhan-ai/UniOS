from assignment_tool import (
    add_assignment_tool,
    get_assignments_tool,
    get_pending_assignments_tool,
    complete_assignment_tool,
    delete_assignment_tool
)


print("\n================================")
print("LANGCHAIN TOOL TEST")
print("================================")


print("\nTool 1:")
print(add_assignment_tool.name)

print("\nTool 2:")
print(get_assignments_tool.name)

print("\nTool 3:")
print(get_pending_assignments_tool.name)

print("\nTool 4:")
print(complete_assignment_tool.name)

print("\nTool 5:")
print(delete_assignment_tool.name)


print("\n================================")
print("TOOLS LOADED SUCCESSFULLY")
print("================================")