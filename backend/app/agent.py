from backend.app.tools.tool_router import detect_intent
import re


# ============================================================
# TOOL INTENTS
# ============================================================

TOOL_INTENTS = {
    "add_assignment",
    "get_assignments",
    "get_quizzes",
    "get_labs",
    "pending_assignments",
    "pending_quizzes",
    "pending_labs",
    "next_deadline",
    "due_today",
    "due_tomorrow",
    "due_this_week",
    "overdue_assignments",
    "next_quiz",
    "next_lab",
    "work_recommendation",
    "course_assignments",
    "refresh_courses",
    "workload_summary",
    "workload",
    "study_planner",
    "study_plan_with_time",
    "next_study_action",
    "complete_current_task",
}


# ============================================================
# SINGLE ACTION DECISION
# ============================================================

def decide_action(user_input: str) -> str:
    """
    Decide whether the request should go to
    RAG or the University tools.
    """

    intent = detect_intent(user_input)

    if intent in TOOL_INTENTS:
        return "tool"

    return "rag"


# ============================================================
# CHECK FOR EXPLICIT STUDY TIME
# ============================================================

def has_available_time(user_input: str) -> bool:
    """
    Check whether the user explicitly mentioned
    an amount of available study time.

    Examples:
        "I have 2 hours"
        "make me a 2-hour study plan"
        "I have 90 minutes"
        "give me a plan for 1.5 hours"
        "make a 30-minute plan"
    """

    import re

    text = user_input.lower()

    # --------------------------------------------------------
    # Hours
    # Supports:
    # 2 hours
    # 2 hour
    # 2-hour
    # 2 hours
    # 1.5 hours
    # --------------------------------------------------------

    hour_pattern = (
        r"\b\d+(?:\.\d+)?\s*-?\s*"
        r"(?:hours?|hrs?|hr)\b"
    )

    if re.search(hour_pattern, text):
        return True

    # --------------------------------------------------------
    # Minutes
    # Supports:
    # 30 minutes
    # 30 minute
    # 30-minute
    # 90 mins
    # --------------------------------------------------------

    minute_pattern = (
        r"\b\d+\s*-?\s*"
        r"(?:minutes?|mins?|min)\b"
    )

    if re.search(minute_pattern, text):
        return True

    return False
# ============================================================
# MULTI-TOOL DECISION
# ============================================================

def decide_multiple_actions(user_input: str) -> list[str]:
    """
    Detect multiple capabilities requested in one message.

    Example:

        "I have 2 hours today and tell me my next deadline"

    returns:

        [
            "study_plan_with_time",
            "next_deadline"
        ]
    """

    text = user_input.lower().strip()

    actions = []

    # ========================================================
    # STUDY PLANNER
    # ========================================================

    study_keywords = [
        "what should i study",
        "what should i study today",
        "study plan",
        "study planner",
        "help me study",
        "plan my study",
        "i have ",
        "make me a plan",
        "make me a study plan",
        "give me a study plan",
    ]

    if any(
        keyword in text
        for keyword in study_keywords
    ):

        # ----------------------------------------------------
        # IMPORTANT:
        # If the user explicitly gives a time,
        # ALWAYS use the time-based planner.
        # ----------------------------------------------------

        if has_available_time(user_input):

            actions.append(
                "study_plan_with_time"
            )

        else:

            actions.append(
                "study_planner"
            )

    # ========================================================
    # DEADLINES
    # ========================================================

    deadline_keywords = [
        "next deadline",
        "deadlines",
        "deadline",
        "due date",
        "due dates",
        "what is due",
        "what's due",
    ]

    if any(
        keyword in text
        for keyword in deadline_keywords
    ):

        intent = detect_intent(
            user_input
        )

        if intent == "next_deadline":

            actions.append(
                "next_deadline"
            )

        elif intent == "due_today":

            actions.append(
                "due_today"
            )

        elif intent == "due_tomorrow":

            actions.append(
                "due_tomorrow"
            )

        elif intent == "due_this_week":

            actions.append(
                "due_this_week"
            )

        else:

            actions.append(
                "next_deadline"
            )

    # ========================================================
    # ASSIGNMENTS
    # ========================================================

    if (
        "show my assignments" in text
        or "my assignments" in text
        or "list assignments" in text
    ):

        actions.append(
            "get_assignments"
        )

    # ========================================================
    # QUIZZES
    # ========================================================

    if (
        "show my quizzes" in text
        or "my quizzes" in text
        or "list quizzes" in text
    ):

        actions.append(
            "get_quizzes"
        )

    # ========================================================
    # LABS
    # ========================================================

    if (
        "show my labs" in text
        or "my labs" in text
        or "list labs" in text
    ):

        actions.append(
            "get_labs"
        )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_actions = []

    for action in actions:

        if action not in unique_actions:

            unique_actions.append(
                action
            )

    # ========================================================
    # FALLBACK
    # ========================================================

    if not unique_actions:

        intent = detect_intent(
            user_input
        )

        if intent in TOOL_INTENTS:

            return [intent]

        return ["rag"]

    return unique_actions