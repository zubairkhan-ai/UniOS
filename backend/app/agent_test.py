from backend.app.agent import (
    decide_action,
    decide_multiple_actions
)


# ============================================================
# TEST QUESTIONS
# ============================================================

tests = [

    "What is TCP?",

    "Show my quizzes",

    "I have 2 hours today",

    "What is my next deadline?",

    "I have 2 hours today and tell me my next deadline",

]


# ============================================================
# RUN TESTS
# ============================================================

for question in tests:

    print()
    print("=" * 60)

    print(
        "Question:",
        question
    )

    # --------------------------------------------------------
    # Single action
    # --------------------------------------------------------

    single = decide_action(
        question
    )

    print(
        "Single decision:",
        single
    )

    # --------------------------------------------------------
    # Multiple actions
    # --------------------------------------------------------

    multiple = decide_multiple_actions(
        question
    )

    print(
        "Multiple decisions:",
        multiple
    )