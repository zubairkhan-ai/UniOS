from typing import TypedDict, Optional


class UniversityState(TypedDict, total=False):

    # ========================================================
    # USER INPUT
    # ========================================================

    user_input: str
    rewritten_input: Optional[str]

    # ========================================================
    # ROUTING
    # ========================================================

    intent: Optional[str]

    route: Optional[str]

    # Multiple actions detected by the agent
    actions: list[str]

    # ========================================================
    # PARAMETERS
    # ========================================================

    parameters: dict

    course: Optional[str]

    week: Optional[str]

    # ========================================================
    # CONVERSATION MEMORY
    # ========================================================

    chat_history: list

    conversation_memory: list
    rag_documents: list

    # ========================================================
    # MULTI-TURN TOOL REQUEST
    #
    # Example:
    #
    # User: add my CN quiz
    #
    # pending_request:
    # {
    #     "intent": "add_assignment",
    #     "parameters": {
    #         "course": "CN",
    #         "title": "Quiz",
    #         "due_date": None,
    #         "task_type": "quiz"
    #     }
    # }
    # ========================================================

    pending_request: Optional[dict]

    # ========================================================
    # CURRENT STUDY TASK
    #
    # Stores the academic task currently recommended
    # by the study planner.
    #
    # Example:
    #
    # current_study_task:
    # {
    #     "id": 8,
    #     "course": "DAA",
    #     "title": "Assignment",
    #     "task_type": "assignment"
    # }
    #
    # This allows the user to say:
    #
    # "I finished this"
    #
    # and the system can understand which task
    # "this" refers to.
    # ========================================================

    current_study_task: Optional[dict]

    # ========================================================
    # RESULTS
    # ========================================================

    # Result from RAG
    rag_result: Optional[str]

    # Result from a single tool
    tool_result: Optional[str]

    # Results from multiple tools
    #
    # Example:
    #
    # [
    #     "You should study Computer Networks...",
    #     "Your next deadline is..."
    # ]
    #
    tool_results: list[str]

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    response: Optional[str]