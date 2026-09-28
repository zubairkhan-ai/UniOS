from .memory import (
    create_memory,
    add_to_memory,
    get_memory,
    clear_memory
)


memory = create_memory()

print("Initial memory:")
print(memory)


memory = add_to_memory(
    memory,
    "What is TCP?",
    "TCP is a transport layer protocol."
)

memory = add_to_memory(
    memory,
    "What are its advantages?",
    "TCP provides reliable and ordered communication."
)


print("\nCurrent memory:")
print(get_memory(memory))


memory = clear_memory()

print("\nAfter clearing:")
print(memory)