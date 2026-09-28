from ..tools.tool_router import detect_intent
from ..tools.assignment_agent import run_assignment_agent
from ..tools.assignment_tool import (
    get_pending_assignments,
    complete_assignment,
)
from backend.app.question_rewriter import rewrite_question
from backend.app.response_generator import generate_response
from ..rag import ask_question
from backend.app.hybrid_router import analyze_query
from backend.app.agent import (
    decide_action,
    decide_multiple_actions
)
from backend.app.rag_query_extractor import extract_rag_query
# ============================================================
# QUESTION REWRITER NODE
# ============================================================

def question_rewriter_node(state):

    user_input = state.get(
        "user_input",
        ""
    )

    conversation_memory = state.get(
        "conversation_memory",
        []
    )

    rewritten_input = rewrite_question(
        user_input,
        conversation_memory
    )

    print("\n[Question Rewriter]")
    print("Original:", user_input)
    print("Rewritten:", rewritten_input)

    return {
        "rewritten_input": rewritten_input
    }
def response_generator_node(state):

    print("\n[Response Generator]")

    route = state.get(
        "route"
    )

    rag_result = state.get(
        "rag_result"
    )

    tool_results = state.get(
        "tool_results",
        []
    )

    # ========================================================
    # PURE RAG
    # ========================================================

    if route == "rag":

        print(
            "[Response Generator] "
            "Returning grounded RAG answer directly."
        )

        return {
            "response": rag_result or "No lecture answer was found."
        }

    # ========================================================
    # PURE TOOL
    # ========================================================

    if route == "tool":

        print(
            "[Response Generator] "
            "Returning tool result directly."
        )

        if tool_results:

            return {
                "response": "\n\n".join(
                    str(result)
                    for result in tool_results
                    if result
                )
            }

        return {
            "response": "No result was found."
        }

    # ========================================================
    # HYBRID
    # ========================================================

    if route == "hybrid":

        print(
            "[Response Generator] "
            "Combining grounded RAG + tool results."
        )

        parts = []

        # ----------------------------
        # RAG RESULT
        # ----------------------------

        if rag_result:

            parts.append(
                f"📚 Lecture Answer:\n{rag_result}"
            )

        # ----------------------------
        # TOOL RESULTS
        # ----------------------------

        if tool_results:

            tool_text = "\n\n".join(
                str(result)
                for result in tool_results
                if result
            )

            if tool_text:

                parts.append(
                    f"📅 University Information:\n{tool_text}"
                )

        # ----------------------------
        # FINAL RESPONSE
        # ----------------------------

        if parts:

            return {
                "response": "\n\n".join(parts)
            }

        return {
            "response": "No result was found."
        }

    # ========================================================
    # FALLBACK
    # ========================================================

    return {
        "response": rag_result or "No response available."
    }
def hybrid_router_node(state):
    """
    Analyze the user's query and determine whether
    RAG, tools, or both are required.
    """

    user_input = state.get("user_input", "")

    analysis = analyze_query(user_input)

    print("\n[Hybrid Router]")
    print("RAG:", analysis["rag"])
    print("Tools:", analysis["tools"])
    print("Actions:", analysis["actions"])

    return {
        "actions": analysis["actions"],
        "route": "hybrid" if (
            analysis["rag"] and analysis["tools"]
        ) else (
            "rag" if analysis["rag"]
            else "tool"
        )
    }
def hybrid_node(state):
    """
    Execute both RAG and tool actions for a hybrid query.
    """

    user_input = state.get("user_input", "")
    actions = state.get("actions", [])

    print("\n[Hybrid Node]")
    print("Actions:", actions)

    # ---------------------------------------------------------
    # Run RAG
    # ---------------------------------------------------------

    rag_result = None

    if "rag" in actions:

    # Extract only the knowledge-related part
        rag_input = state.get(
            "rewritten_input"
        ) or user_input
        rag_query = extract_rag_query(
             rag_input
        )

        print("\n[Hybrid RAG]")
        print("Original query:", user_input)
        print("RAG query:", rag_query)

        rag_state = dict(state)

        # Give RAG only the extracted question
        rag_state["user_input"] = rag_query
        rag_state["route"] = "rag"

        rag_output = rag_node(rag_state)

        rag_result = rag_output.get(
            "response",
            rag_output.get("rag_result", "")
    )

    # ---------------------------------------------------------
    # Run tools
    # ---------------------------------------------------------

    tool_results = []

    tool_actions = [
        action
        for action in actions
        if action != "rag"
    ]

    if tool_actions:

        tool_state = dict(state)

        tool_state["actions"] = tool_actions
        tool_state["route"] = "tool"

        tool_output = tool_node(tool_state)

        tool_results = tool_output.get(
            "tool_results",
            []
        )

    # ---------------------------------------------------------
    # Combine results
    # ---------------------------------------------------------

    combined_parts = []

    if rag_result:
        combined_parts.append(
            f"📚 KNOWLEDGE ANSWER\n\n{rag_result}"
        )

    if tool_results:
        combined_parts.extend(tool_results)

    response = "\n\n".join(combined_parts)

    return {
        "rag_result": rag_result,
        "tool_results": tool_results,
        "tool_result": "\n\n".join(tool_results),
        "response": response,
        "route": "hybrid",
    }
# ============================================================
# ROUTER NODE
# ============================================================

def router_node(state):

    user_input = state["user_input"]

    pending_request = state.get("pending_request")

    # --------------------------------------------------------
    # Handle pending multi-turn tool request
    # --------------------------------------------------------

    if pending_request is not None:

        print("\n[Router] Pending tool request detected")

        pending_intent = pending_request.get(
            "intent",
            "add_assignment"
        )

        return {
            "intent": pending_intent,
            "route": "tool",
            "actions": [pending_intent]
        }

    # --------------------------------------------------------
    # Detect multiple actions
    # --------------------------------------------------------

    actions = decide_multiple_actions(user_input)

    print(
        f"\n[Agent] Actions: {actions}"
    )

    # --------------------------------------------------------
    # RAG request
    # --------------------------------------------------------

    if actions == ["rag"]:

        return {
            "intent": "rag",
            "route": "rag",
            "actions": ["rag"]
        }

    # --------------------------------------------------------
    # Tool request
    # --------------------------------------------------------

    intent = decide_action(user_input)

    print(
        f"[Agent] Decision: {intent}"
    )

    # IMPORTANT:
    # decide_multiple_actions() may not know about
    # complete_current_task yet.
    #
    # Therefore we explicitly use detect_intent()
    # for this conversational action.

    if intent == "complete_current_task":

        return {
            "intent": "complete_current_task",
            "route": "tool",
            "actions": ["complete_current_task"]
        }

    return {
        "intent": intent,
        "route": "tool",
        "actions": actions
    }


# ============================================================
# EXTRACT AVAILABLE STUDY TIME
# ============================================================

def extract_available_minutes(user_input):

    import re

    text = user_input.lower()

    # --------------------------------------------------------
    # Hours
    # --------------------------------------------------------

    hour_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*-?\s*(?:hours?|hrs?|hr)\b",
        text
    )

    if hour_match:

        hours = float(
            hour_match.group(1)
        )

        return int(
            hours * 60
        )

    # --------------------------------------------------------
    # Minutes
    # --------------------------------------------------------

    minute_match = re.search(
        r"\b(\d+)\s*-?\s*(?:minutes?|mins?|min)\b",
        text
    )

    if minute_match:

        return int(
            minute_match.group(1)
        )

    return None


# ============================================================
# RESPONSE FORMATTERS
# ============================================================

def format_deadline(result):
    """
    Convert raw deadline dictionary into a clean response.
    """

    if not result:
        return "📌 NEXT DEADLINE\nNo upcoming deadlines found."

    if not isinstance(result, dict):
        return f"📌 NEXT DEADLINE\n{result}"

    course = result.get(
        "course",
        "Unknown course"
    )

    title = result.get(
        "title",
        "Untitled"
    )

    due_date = result.get(
        "due_date",
        "Unknown"
    )

    status = result.get(
        "status",
        "unknown"
    ).capitalize()

    task_type = result.get(
        "task_type",
        "assignment"
    ).capitalize()

    return (
        "📌 NEXT DEADLINE\n"
        f"{course} — {title}\n"
        f"Type: {task_type}\n"
        f"Due: {due_date}\n"
        f"Status: {status}"
    )


def format_study_plan(result):
    """
    Add a clean heading to the study planner output.
    """

    return (
        "📚 STUDY PLAN\n"
        f"{result}"
    )


def format_task_list(result, heading):
    """
    Add a clean heading to assignment/quiz/lab lists.
    """

    return (
        f"{heading}\n"
        f"{result}"
    )


# ============================================================
# GET CURRENT STUDY TASK
# ============================================================

def get_current_study_task():
    """
    Get the first pending academic task.

    This task is stored in LangGraph state so that a later
    message such as "I finished this" can refer to it.
    """

    tasks = get_pending_assignments()

    if not tasks:
        return None

    return tasks[0]


# ============================================================
# COMPLETE CURRENT STUDY TASK
# ============================================================

def complete_current_study_task(current_study_task):
    """
    Mark the task remembered by the study planner as completed.
    """

    # --------------------------------------------------------
    # No remembered task
    # --------------------------------------------------------

    if not current_study_task:

        return (
            "I don't have a current study task in memory. "
            "Ask me for a study plan first."
        )

    # --------------------------------------------------------
    # Get task information
    # --------------------------------------------------------

    task_id = current_study_task.get(
        "id"
    )

    course = current_study_task.get(
        "course",
        "Unknown course"
    )

    title = current_study_task.get(
        "title",
        "Untitled"
    )

    # --------------------------------------------------------
    # Validate task ID
    # --------------------------------------------------------

    if task_id is None:

        return (
            "I found the current study task, "
            "but I couldn't find its database ID."
        )

    # --------------------------------------------------------
    # Complete task in SQLite
    # --------------------------------------------------------

    result = complete_assignment(
        task_id
    )

    print(
        "\n[DEBUG] Completing current study task:"
    )

    print(
        "Task ID:",
        task_id
    )

    print(
        "Result:",
        result
    )

    # --------------------------------------------------------
    # Return clean confirmation
    # --------------------------------------------------------

    return (
        f"✅ TASK COMPLETED\n\n"
        f"{course} — {title}\n"
        f"Task ID: {task_id}\n\n"
        f"Nice work! 🎉"
    )


# ============================================================
# TOOL NODE
# ============================================================

def tool_node(state):

    user_input = state["user_input"]

    pending_request = state.get(
        "pending_request"
    )

    current_study_task = state.get(
        "current_study_task"
    )

    actions = state.get(
        "actions",
        []
    )

    # --------------------------------------------------------
    # Fallback to single intent
    # --------------------------------------------------------

    if not actions:

        intent = state.get(
            "intent"
        )

        if intent:

            actions = [intent]

    # --------------------------------------------------------
    # SINGLE TOOL
    # --------------------------------------------------------

    if len(actions) == 1:

        action = actions[0]

        # ====================================================
        # COMPLETE CURRENT STUDY TASK
        # ====================================================

        if action == "complete_current_task":

            response = complete_current_study_task(
                current_study_task
            )

            return {
                "tool_result": response,

                "tool_results": [
                    response
                ],

                "response": response,

                "pending_request":
                    None,

                # Task is completed, so clear it
                "current_study_task":
                    None
            }

        # ====================================================
        # STUDY PLAN WITH SPECIFIC TIME
        # ====================================================

        if action == "study_plan_with_time":

            from ..tools.study_planner import (
                study_plan_with_time
            )

            available_minutes = (
                extract_available_minutes(
                    user_input
                )
            )

            if available_minutes is None:

                response = (
                    "I couldn't determine "
                    "how much study time you have."
                )

                return {
                    "tool_result": response,

                    "tool_results": [
                        response
                    ],

                    "response": response,

                    "pending_request":
                        pending_request,

                    "current_study_task":
                        current_study_task
                }

            # ------------------------------------------------
            # Generate study plan
            # ------------------------------------------------

            result = study_plan_with_time.invoke(
                {
                    "available_minutes":
                        available_minutes
                }
            )

            # ------------------------------------------------
            # Remember current study task
            # ------------------------------------------------

            updated_study_task = (
                get_current_study_task()
            )

            print(
                "\n[DEBUG] Current study task:"
            )

            print(
                updated_study_task
            )

            response = format_study_plan(
                str(result)
            )

            return {
                "tool_result": response,

                "tool_results": [
                    response
                ],

                "response": response,

                "pending_request":
                    pending_request,

                "current_study_task":
                    updated_study_task
            }

        # ====================================================
        # GENERAL STUDY PLANNER
        # ====================================================

        elif action == "study_planner":

            from ..tools.study_planner import (
                study_planner
            )

            result = study_planner.invoke({})

            # ------------------------------------------------
            # Remember current study task
            # ------------------------------------------------

            updated_study_task = (
                get_current_study_task()
            )

            print(
                "\n[DEBUG] Current study task:"
            )

            print(
                updated_study_task
            )

            response = format_study_plan(
                str(result)
            )

            return {
                "tool_result": response,

                "tool_results": [
                    response
                ],

                "response": response,

                "pending_request":
                    pending_request,

                "current_study_task":
                    updated_study_task
            }

        # ====================================================
        # ALL OTHER SINGLE TOOLS
        # ====================================================

        else:

            result = run_assignment_agent(
                user_input,
                pending_request
            )

            print(
                "\n[DEBUG] assignment_agent result:"
            )

            print(
                result
            )

            return {
                "tool_result":
                    result["response"],

                "tool_results": [
                    result["response"]
                ],

                "response":
                    result["response"],

                "pending_request":
                    result.get(
                        "pending_request"
                    ),

                "current_study_task":
                    current_study_task
            }

    # --------------------------------------------------------
    # MULTIPLE TOOLS
    # --------------------------------------------------------

    results = []

    # Keep previous study task unless a new
    # study plan is generated.

    updated_study_task = (
        current_study_task
    )

    for action in actions:

        print(
            f"\n[Multi-Agent] Executing tool: {action}"
        )

        # ====================================================
        # COMPLETE CURRENT STUDY TASK
        # ====================================================

        if action == "complete_current_task":

            response = complete_current_study_task(
                updated_study_task
            )

            results.append(
                response
            )

            # Task is completed
            updated_study_task = None

        # ====================================================
        # STUDY PLAN WITH SPECIFIC TIME
        # ====================================================

        elif action == "study_plan_with_time":

            from ..tools.study_planner import (
                study_plan_with_time
            )

            available_minutes = (
                extract_available_minutes(
                    user_input
                )
            )

            if available_minutes is None:

                result = (
                    "I couldn't determine "
                    "how much study time you have."
                )

            else:

                result = (
                    study_plan_with_time.invoke(
                        {
                            "available_minutes":
                                available_minutes
                        }
                    )
                )

                # --------------------------------------------
                # Remember the first task in the plan
                # --------------------------------------------

                updated_study_task = (
                    get_current_study_task()
                )

                if updated_study_task:

                    print(
                        "\n[DEBUG] Current study task:"
                    )

                    print(
                        updated_study_task
                    )

            formatted = format_study_plan(
                str(result)
            )

            results.append(
                formatted
            )

        # ====================================================
        # GENERAL STUDY PLANNER
        # ====================================================

        elif action == "study_planner":

            from ..tools.study_planner import (
                study_planner
            )

            result = study_planner.invoke({})

            # --------------------------------------------
            # Remember the first pending task
            # --------------------------------------------

            updated_study_task = (
                get_current_study_task()
            )

            if updated_study_task:

                print(
                    "\n[DEBUG] Current study task:"
                )

                print(
                    updated_study_task
                )

            formatted = format_study_plan(
                str(result)
            )

            results.append(
                formatted
            )

        # ====================================================
        # NEXT DEADLINE
        # ====================================================

        elif action == "next_deadline":

            from ..tools.deadline_tool import (
                get_next_deadline
            )

            result = get_next_deadline()

            formatted = format_deadline(
                result
            )

            results.append(
                formatted
            )

        # ====================================================
        # ASSIGNMENTS
        # ====================================================

        elif action == "get_assignments":

            result = run_assignment_agent(
                "show my assignments",
                None
            )

            formatted = format_task_list(
                result["response"],
                "📚 ASSIGNMENTS"
            )

            results.append(
                formatted
            )

        # ====================================================
        # QUIZZES
        # ====================================================

        elif action == "get_quizzes":

            result = run_assignment_agent(
                "show my quizzes",
                None
            )

            formatted = format_task_list(
                result["response"],
                "📝 QUIZZES"
            )

            results.append(
                formatted
            )

        # ====================================================
        # LABS
        # ====================================================

        elif action == "get_labs":

            result = run_assignment_agent(
                "show my labs",
                None
            )

            formatted = format_task_list(
                result["response"],
                "🧪 LABS"
            )

            results.append(
                formatted
            )

        # ====================================================
        # OTHER TOOLS
        # ====================================================

        else:

            result = run_assignment_agent(
                user_input,
                pending_request
            )

            results.append(
                result["response"]
            )

    # --------------------------------------------------------
    # Combine multi-tool results
    # --------------------------------------------------------

    combined_response = "\n\n".join(
        results
    )

    return {
        "tool_result":
            combined_response,

        "tool_results":
            results,

        "response":
            combined_response,

        "pending_request":
            pending_request,

        "current_study_task":
            updated_study_task
    }


# ============================================================
# RAG NODE
# ============================================================

def rag_node(state):

    user_input = (
        state.get("rewritten_input")
        or state["user_input"]
    )

    print("\n[RAG] Processing question...")

    result = ask_question(
        user_input
    )

    # ask_question returns:
    # (answer, documents)

    if isinstance(result, tuple):

        answer = result[0]
        documents = result[1]

    else:

        answer = result
        documents = []

    return {
        "rag_result": answer,
        "rag_documents": documents,
        "response": answer
    }