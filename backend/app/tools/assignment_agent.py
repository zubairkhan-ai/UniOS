import re

from .tool_router import (
    detect_intent,
    execute_tool
)

from .parameter_extractor import (
    extract_course,
    extract_title,
    extract_due_date,
    extract_description,
    extract_task_type,
    extract_available_minutes
)


# ============================================================
# FORMAT SINGLE TASK
# ============================================================

def format_single_task(task):

    if not task:
        return "No task found."

    task_type = task.get(
        "task_type",
        "assignment"
    ).lower()

    icons = {
        "assignment": "📘",
        "quiz": "📝",
        "lab": "🧪"
    }

    icon = icons.get(
        task_type,
        "📌"
    )

    return (
        f"[{task.get('id', '?')}] "
        f"{icon} "
        f"{task.get('course', '?')} - "
        f"{task.get('title', '?')}\n"
        f"    Type: {task_type.capitalize()}\n"
        f"    Due: {task.get('due_date', '?')}\n"
        f"    Status: {task.get('status', '?')}"
    )


# ============================================================
# FORMAT TASK LIST
# ============================================================

def format_task_list(tasks):

    if not tasks:
        return "No tasks found."

    return "\n".join(
        format_single_task(task)
        for task in tasks
    )


# ============================================================
# FORMAT TOOL RESULT
# ============================================================

def format_tool_result(result):

    if result is None:
        return "No matching task found."

    # --------------------------------------------------------
    # STRING RESULT
    # --------------------------------------------------------

    if isinstance(result, str):
        return result

    # --------------------------------------------------------
    # MESSAGE DICTIONARY
    # --------------------------------------------------------

    if (
        isinstance(result, dict)
        and "message" in result
        and "course" not in result
    ):

        return result["message"]

    # --------------------------------------------------------
    # SUCCESSFULLY ADDED TASK
    # --------------------------------------------------------

    if (
        isinstance(result, dict)
        and result.get("success")
        and "course" in result
        and "title" in result
    ):

        task_type = result.get(
            "task_type",
            "assignment"
        )

        icons = {
            "assignment": "📘",
            "quiz": "📝",
            "lab": "🧪"
        }

        icon = icons.get(
            task_type,
            "📌"
        )

        return (
            f"✅ {icon} "
            f"{task_type.capitalize()} added successfully.\n\n"
            f"Course: {result['course']}\n"
            f"Title: {result['title']}\n"
            f"Due: {result['due_date']}\n"
            f"Status: {result['status']}"
        )

    # --------------------------------------------------------
    # SINGLE TASK
    # --------------------------------------------------------

    if (
        isinstance(result, dict)
        and "course" in result
        and "title" in result
        and "due_date" in result
    ):

        return format_single_task(
            result
        )

    # --------------------------------------------------------
    # TASK LIST
    # --------------------------------------------------------

    if isinstance(result, list):

        if not result:
            return "No tasks found."

        return format_task_list(
            result
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return str(result)


# ============================================================
# EXTRACT TASK ID
# ============================================================

def extract_assignment_id(text):

    patterns = [
        r"\b(?:id|assignment|task)\s*#?\s*(\d+)\b",
        r"#(\d+)\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return int(
                match.group(1)
            )

    return None


# ============================================================
# CHECK IF TEXT IS ONLY A DATE
# ============================================================

def is_date_only(text):

    text = text.strip().lower()

    # today / tomorrow
    if text in {
        "today",
        "tomorrow"
    }:

        return True

    # in X days
    if re.fullmatch(
        r"in\s+\d+\s+days?",
        text
    ):

        return True

    # ISO date
    if re.fullmatch(
        r"\d{4}-\d{1,2}-\d{1,2}",
        text
    ):

        return True

    # 27 September
    if re.fullmatch(
        r"\d{1,2}\s+[a-zA-Z]+",
        text
    ):

        return True

    # September 27
    if re.fullmatch(
        r"[a-zA-Z]+\s+\d{1,2}",
        text
    ):

        return True

    # 09/27/2026
    if re.fullmatch(
        r"\d{1,2}/\d{1,2}/\d{2,4}",
        text
    ):

        return True

    return False


# ============================================================
# GENERIC TITLE CHECK
# ============================================================

def is_generic_title(title):

    if not title:
        return False

    generic_titles = {
        "quiz",
        "lab",
        "assignment",
        "homework",
        "task"
    }

    return (
        title.strip().lower()
        in generic_titles
    )


# ============================================================
# ASSIGNMENT / TASK AGENT
# ============================================================

def run_assignment_agent(
    user_input,
    pending_request=None
):

    text = user_input.strip()

    # ========================================================
    # MULTI-TURN ADD REQUEST
    # ========================================================

    if (
        pending_request
        and pending_request.get("intent")
        == "add_assignment"
    ):

        # ----------------------------------------------------
        # Copy previous parameters
        # ----------------------------------------------------

        parameters = dict(
            pending_request.get(
                "parameters",
                {}
            )
        )

        # ====================================================
        # COURSE
        # ====================================================

        if not parameters.get("course"):

            new_course = extract_course(
                text
            )

            if new_course:

                parameters["course"] = (
                    new_course
                )

        # ====================================================
        # TASK TYPE
        # ====================================================

        # Only update task type when the user explicitly
        # mentions one.

        lower_text = text.lower()

        if any(
            word in lower_text
            for word in [
                "quiz",
                "lab",
                "assignment",
                "homework"
            ]
        ):

            new_task_type = extract_task_type(
                text
            )

            if new_task_type:

                parameters["task_type"] = (
                    new_task_type
                )

        # ====================================================
        # DUE DATE
        # ====================================================

        new_due_date = extract_due_date(
            text
        )

        if new_due_date:

            parameters["due_date"] = (
                new_due_date
            )

        # ====================================================
        # DESCRIPTION
        # ====================================================

        new_description = extract_description(
            text
        )

        if new_description:

            parameters["description"] = (
                new_description
            )

        # ====================================================
        # TITLE
        # ====================================================

        if not parameters.get("title"):

            # If this response is not a date,
            # use it as the title.

            if not is_date_only(text):

                # Do not use generic task-type words
                # as titles.

                if not is_generic_title(text):

                    parameters["title"] = text

        # ====================================================
        # FIND MISSING FIELDS
        # ====================================================

        missing = []

        if not parameters.get("course"):

            missing.append(
                "course"
            )

        if not parameters.get("title"):

            missing.append(
                "title"
            )

        if not parameters.get("due_date"):

            missing.append(
                "due date"
            )

        # ====================================================
        # ASK FOR MISSING FIELD
        # ====================================================

        if missing:

            next_field = missing[0]

            # -----------------------------------------------
            # Course
            # -----------------------------------------------

            if next_field == "course":

                question = (
                    "Which course is it for?"
                )

            # -----------------------------------------------
            # Title
            # -----------------------------------------------

            elif next_field == "title":

                task_type = parameters.get(
                    "task_type",
                    "assignment"
                )

                if task_type == "quiz":

                    question = (
                        "What is the quiz title?"
                    )

                elif task_type == "lab":

                    question = (
                        "What is the lab title?"
                    )

                elif task_type == "assignment":

                    question = (
                        "What is the assignment title?"
                    )

                else:

                    question = (
                        "What is the title?"
                    )

            # -----------------------------------------------
            # Due date
            # -----------------------------------------------

            elif next_field == "due date":

                question = (
                    "What is the due date?"
                )

            else:

                question = (
                    "Please provide the missing information."
                )

            return {

                "response":
                    question,

                "pending_request": {

                    "intent":
                        "add_assignment",

                    "parameters":
                        parameters
                }
            }

        # ====================================================
        # ALL INFORMATION AVAILABLE
        # ====================================================

        result = execute_tool(
            "add_assignment",
            parameters
        )

        return {

            "response":
                format_tool_result(
                    result
                ),

            "pending_request":
                None
        }

    # ========================================================
    # NEW REQUEST
    # ========================================================

    intent = detect_intent(
        user_input
    )

    # ========================================================
    # ADD ASSIGNMENT / QUIZ / LAB
    # ========================================================

    if intent == "add_assignment":

        # ----------------------------------------------------
        # Extract all available information
        # ----------------------------------------------------

        course = extract_course(
            user_input
        )

        title = extract_title(
            user_input
        )

        due_date = extract_due_date(
            user_input
        )

        description = extract_description(
            user_input
        )

        task_type = extract_task_type(
            user_input
        )

        # ----------------------------------------------------
        # IMPORTANT FIX
        #
        # "quiz" / "lab" / "assignment" alone should NOT
        # become the title.
        #
        # Example:
        #
        # add my OS quiz
        #
        # becomes:
        #
        # course    = OS
        # title     = None
        # task_type = quiz
        # due_date  = None
        # ----------------------------------------------------

        if is_generic_title(title):

            title = None

        # ----------------------------------------------------
        # Build parameters
        # ----------------------------------------------------

        parameters = {

            "course":
                course,

            "title":
                title,

            "due_date":
                due_date,

            "description":
                description,

            "task_type":
                task_type
        }

        # ====================================================
        # FIND MISSING PARAMETERS
        # ====================================================

        missing = []

        if not parameters["course"]:

            missing.append(
                "course"
            )

        if not parameters["title"]:

            missing.append(
                "title"
            )

        if not parameters["due_date"]:

            missing.append(
                "due date"
            )

        # ====================================================
        # ASK FOR MISSING PARAMETER
        # ====================================================

        if missing:

            next_field = missing[0]

            # ------------------------------------------------
            # COURSE
            # ------------------------------------------------

            if next_field == "course":

                question = (
                    "Which course is it for?"
                )

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            elif next_field == "title":

                if task_type == "quiz":

                    question = (
                        "What is the quiz title?"
                    )

                elif task_type == "lab":

                    question = (
                        "What is the lab title?"
                    )

                elif task_type == "assignment":

                    question = (
                        "What is the assignment title?"
                    )

                else:

                    question = (
                        "What is the title?"
                    )

            # ------------------------------------------------
            # DUE DATE
            # ------------------------------------------------

            elif next_field == "due date":

                question = (
                    "What is the due date?"
                )

            else:

                question = (
                    "Please provide the missing information."
                )

            return {

                "response":
                    question,

                "pending_request": {

                    "intent":
                        "add_assignment",

                    "parameters":
                        parameters
                }
            }

        # ====================================================
        # CREATE TASK
        # ====================================================

        result = execute_tool(
            "add_assignment",
            parameters
        )

        return {

            "response":
                format_tool_result(
                    result
                ),

            "pending_request":
                None
        }

    # ========================================================
    # COMPLETE TASK
    # ========================================================

    if intent == "complete_assignment":

        assignment_id = extract_assignment_id(
            user_input
        )

        if not assignment_id:

            return {

                "response":
                    (
                        "Please provide the task ID. "
                        "Example: complete task 7"
                    ),

                "pending_request":
                    None
            }

        result = execute_tool(
            "complete_assignment",
            {
                "assignment_id":
                    assignment_id
            }
        )

        return {

            "response":
                format_tool_result(
                    result
                ),

            "pending_request":
                None
        }

    # ========================================================
    # DELETE TASK
    # ========================================================

    if intent == "delete_assignment":

        assignment_id = extract_assignment_id(
            user_input
        )

        if not assignment_id:

            return {

                "response":
                    (
                        "Please provide the task ID. "
                        "Example: delete task 7"
                    ),

                "pending_request":
                    None
            }

        result = execute_tool(
            "delete_assignment",
            {
                "assignment_id":
                    assignment_id
            }
        )

        return {

            "response":
                format_tool_result(
                    result
                ),

            "pending_request":
                None
        }

    # ========================================================
    # OTHER TOOL REQUESTS
    # ========================================================

    parameters = {}

    # --------------------------------------------------------
    # COURSE
    # --------------------------------------------------------

    course = extract_course(
        user_input
    )

    if course:

        parameters["course"] = (
            course
        )

    # --------------------------------------------------------
    # AVAILABLE STUDY TIME
    #
    # IMPORTANT:
    # This fixes:
    #
    # "I have 90 minutes today"
    # "I have 3 hours to study"
    # "I have 1.5 hours"
    #
    # The extracted value is passed to:
    # study_plan_with_time
    # --------------------------------------------------------

    available_minutes = extract_available_minutes(
        user_input
    )

    if available_minutes is not None:

        parameters["available_minutes"] = (
            available_minutes
        )

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print(
        "\n[DEBUG] Tool intent:",
        intent
    )

    print(
        "[DEBUG] Tool parameters:",
        parameters
    )

    # --------------------------------------------------------
    # EXECUTE TOOL
    # --------------------------------------------------------

    result = execute_tool(
        intent,
        parameters
    )

    return {

        "response":
            format_tool_result(
                result
            ),

        "pending_request":
            None
    }