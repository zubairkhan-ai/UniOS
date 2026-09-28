import re

from backend.app.agent import decide_multiple_actions


def needs_rag(user_input: str) -> bool:
    """
    Decide whether the user's query needs the RAG knowledge base.
    """

    text = user_input.lower().strip()

    # Explicit knowledge/learning questions
    rag_patterns = [
        r"\bwhat is\b",
        r"\bwhat are\b",
        r"\bwho is\b",
        r"\bexplain\b",
        r"\bdefine\b",
        r"\bdefinition of\b",
        r"\bhow does\b",
        r"\bhow do\b",
        r"\bwhy does\b",
        r"\bwhy is\b",
        r"\bmeaning of\b",
        r"\btell me about\b",
        r"\bdescribe\b",
        r"\bdifference between\b",
        r"\bcompare\b",
        r"\bwhat about\b",
    ]

    for pattern in rag_patterns:
        if re.search(pattern, text):
            return True

    return False


def analyze_query(user_input: str) -> dict:
    """
    Analyze a user query and decide whether it needs
    RAG, tools, or both.
    """

    actions = decide_multiple_actions(user_input)

    rag_required = needs_rag(user_input)

    # If the normal agent didn't detect any tool
    # and RAG is not required, fall back to RAG.
    if not actions:
        actions = ["rag"]

    # Remove the old generic RAG action if we are
    # explicitly handling RAG separately.
    tool_actions = [
        action for action in actions
        if action != "rag"
    ]

    return {
        "rag": rag_required,
        "tools": tool_actions,
        "actions": (
            ["rag"] if rag_required else []
        ) + tool_actions
    }


if __name__ == "__main__":

    tests = [
        "What is TCP?",
        "Show my quizzes",
        "What is TCP and tell me my next deadline",
        "Explain subnetting and show my quizzes",
        "I have 2 hours today",
        "Explain TCP, show my quizzes and make me a 2 hour study plan",
    ]

    for question in tests:
        print("\n" + "=" * 70)
        print("QUESTION:", question)
        print("ANALYSIS:", analyze_query(question))