from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .memory import (
    create_memory,
    add_to_memory,
    get_rag_memory,
    clear_memory
)

from .state_store import (
    load_state,
    save_state,
    clear_state
)
from .state import UniversityState

from .nodes import (
    router_node,
    tool_node,
    rag_node,
    hybrid_router_node,
    hybrid_node,
    response_generator_node,
    question_rewriter_node,
)

# ============================================================
# ROUTE REQUEST
# ============================================================

def route_request(state):

    route = state.get("route")

    if route == "hybrid":
        return "hybrid"

    if route == "tool":
        return "tool"

    return "rag"
#==========================================
# BUILD LANGGRAPH
# ============================================================

builder = StateGraph(
    UniversityState
)


# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------
builder.add_node(
    "response_generator",
    response_generator_node
)
builder.add_node(
    "router",
    router_node
)

builder.add_node(
    "tool",
    tool_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "hybrid_router",
    hybrid_router_node
)
builder.add_node(
    "hybrid",
    hybrid_node
)
# ------------------------------------------------------------
# Starting point
# ------------------------------------------------------------
builder.add_edge(
    START,
    "question_rewriter"
)
builder.add_edge(
    "question_rewriter",
    "hybrid_router"
)
builder.add_node(
    "question_rewriter",
    question_rewriter_node
)

# ------------------------------------------------------------
# Conditional routing
# ------------------------------------------------------------

builder.add_conditional_edges(
    "hybrid_router",
    route_request,
    {
        "tool": "tool",
        "rag": "rag",
        "hybrid": "hybrid"
    }
)

# ------------------------------------------------------------
# End points
# ------------------------------------------------------------

builder.add_edge("tool", "response_generator")
builder.add_edge("rag", "response_generator")
builder.add_edge("hybrid", "response_generator")

builder.add_edge("response_generator", END)
# ------------------------------------------------------------
# Compile graph
# ------------------------------------------------------------

university_graph = builder.compile()


# ============================================================
# PERSISTENT MEMORY
# ============================================================

conversation_memory = create_memory()

# Used for multi-turn requests such as:
#
# You: add my CN quiz
# AI: What is the title?
# You: TCP Quiz
# AI: What is the due date?
# You: tomorrow




# ============================================================
# CURRENT STUDY TASK
# ============================================================
#
# Stores the academic task currently recommended by
# the study planner.
#
# Example:
#
# {
#     "id": 8,
#     "course": "DAA",
#     "title": "Assignment",
#     "task_type": "assignment"
# }
#
# This allows:
#
# You: I finished this
#
# to refer to the task that was previously recommended.
# ============================================================
# ============================================================
# PERSISTENT APPLICATION STATE
# ============================================================

_saved_state = load_state()

pending_request = _saved_state.get(
    "pending_request"
)

current_study_task = _saved_state.get(
    "current_study_task"
)

# ============================================================
# CHAT
# ============================================================

def chat(user_input):

    global conversation_memory
    global pending_request
    global current_study_task

    # --------------------------------------------------------
    # RAG should ONLY see RAG conversations
    # --------------------------------------------------------

    rag_memory = get_rag_memory(
        conversation_memory
    )

    # --------------------------------------------------------
    # Run LangGraph
    # --------------------------------------------------------

    result = university_graph.invoke(
        {
            "user_input": user_input,

            "parameters": {},

            "chat_history":
                rag_memory,

            "conversation_memory":
                conversation_memory,

            "pending_request":
                pending_request,

            "current_study_task":
                current_study_task,

            "course": None,

            "week": None,

            # ------------------------------------------------
            # Multi-tool state
            # ------------------------------------------------

            "actions": [],

            "tool_results": []
        }
    )

    # --------------------------------------------------------
    # Get response
    # --------------------------------------------------------

    response = result.get(
        "response",
        "No response"
    )

    # --------------------------------------------------------
    # Get route and intent
    # --------------------------------------------------------

    route = result.get(
        "route"
    )

    intent = result.get(
        "intent"
    )

    # --------------------------------------------------------
    # Get actions
    # --------------------------------------------------------

    actions = result.get(
        "actions",
        []
    )

    # --------------------------------------------------------
    # Get multiple tool results
    # --------------------------------------------------------

    tool_results = result.get(
        "tool_results",
        []
    )

    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print(
        "\n[DEBUG] actions:",
        actions
    )

    print(
        "[DEBUG] tool_results:",
        tool_results
    )

    # --------------------------------------------------------
    # Preserve pending request
    # --------------------------------------------------------

    pending_request = result.get(
        "pending_request"
    )

    print(
        "[DEBUG] pending_request:",
        pending_request
    )

    # --------------------------------------------------------
    # Preserve current study task
    # --------------------------------------------------------

    current_study_task = result.get(
        "current_study_task",
        current_study_task
    )

    print(
        "[DEBUG] current_study_task:",
        current_study_task
    )
# --------------------------------------------------------
# SAVE PERSISTENT APPLICATION STATE
# --------------------------------------------------------

    save_state(
        current_study_task=current_study_task,
        pending_request=pending_request
    )
    # --------------------------------------------------------
    # Decide memory type
    # --------------------------------------------------------

    if route == "tool":

        memory_type = "tool"

    else:

        memory_type = "rag"

    # --------------------------------------------------------
    # Save conversation
    # --------------------------------------------------------

    conversation_memory = add_to_memory(
        conversation_memory,
        user_input,
        response,
        memory_type=memory_type,
        intent=intent
    )

    return response


# ============================================================
# CLEAR MEMORY
# ============================================================

def global_memory_clear():

    global conversation_memory
    global pending_request
    global current_study_task

    conversation_memory = clear_memory()

    pending_request = None

    current_study_task = None


# ============================================================
# INTERACTIVE CHAT
# ============================================================

def run_chat():

    print()

    print("=" * 60)
    print("🎓 AI UNIVERSITY OS")
    print("LangGraph + RAG + Tools + Memory")
    print("=" * 60)

    print()

    print("Type your question below.")
    print("Type 'exit' to quit.")
    print("Type 'memory' to view memory.")
    print("Type 'clear' to clear memory.")

    print()

    while True:

        try:

            user_input = input(
                "You: "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError
        ):

            print()
            print("Goodbye 👋")

            break

        # ----------------------------------------------------
        # Ignore empty input
        # ----------------------------------------------------

        if not user_input:

            continue

        # ----------------------------------------------------
        # Remove accidental "You:" prefix
        # ----------------------------------------------------

        if user_input.lower().startswith("you:"):

            user_input = user_input[4:].strip()

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() == "exit":

            print()
            print("Goodbye 👋")

            break

        # ----------------------------------------------------
        # SHOW MEMORY
        # ----------------------------------------------------

        if user_input.lower() == "memory":

            print()

            print("=" * 60)
            print("CURRENT MEMORY")
            print("=" * 60)

            if not conversation_memory:

                print(
                    "Memory is empty."
                )

            else:

                for index, message in enumerate(
                    conversation_memory,
                    start=1
                ):

                    print()

                    print(
                        f"Conversation {index}"
                    )

                    print(
                        "Type:",
                        message.get(
                            "type",
                            "unknown"
                        )
                    )

                    if message.get("intent"):

                        print(
                            "Intent:",
                            message["intent"]
                        )

                    print(
                        "User:",
                        message.get(
                            "user",
                            ""
                        )
                    )

                    print(
                        "AI:",
                        message.get(
                            "ai",
                            ""
                        )
                    )

            print()

            continue

        # ----------------------------------------------------
        # CLEAR MEMORY
        # ----------------------------------------------------

        if user_input.lower() == "clear":

            global_memory_clear()

            print()

            print(
                "🧹 Conversation memory cleared."
            )

            print()

            continue

        # ----------------------------------------------------
        # NORMAL CHAT
        # ----------------------------------------------------

        print()

        answer = chat(
            user_input
        )

        print()

        print("AI:")

        print(answer)

        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_chat()