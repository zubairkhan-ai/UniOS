import re

from .assignment_tool import (
    add_assignment,
    get_assignments,
    get_pending_assignments,
    complete_assignment,
    delete_assignment,
    refresh_courses,
    get_tasks_by_type,
    get_pending_tasks_by_type,
)

from .deadline_tool import (
    get_due_today,
    get_due_tomorrow,
    get_due_this_week,
    get_overdue_assignments,
    get_next_deadline,
    get_course_assignments,
    get_work_recommendations,
)

from .workload_tool import (
    format_workload_summary,
)

from .parameter_extractor import (
    extract_course,
    extract_title,
    extract_due_date,
    extract_description,
    extract_task_type,
    extract_available_minutes,
)

from .study_planner import (
    study_planner,
    study_plan_with_time,
    next_study_action,
)


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):

    text_lower = text.lower().strip()

    # ========================================================
    # REFRESH COURSES
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "refresh courses",
            "sync courses",
            "update courses",
            "rescan courses",
        ]
    ):
        return "refresh_courses"


    # ========================================================
    # WORKLOAD
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "show my workload",
            "workload summary",
            "academic workload",
            "how many assignments do i have",
            "how much work do i have",
            "my workload",
        ]
    ):
        return "workload_summary"


    # ========================================================
    # STUDY PLANNER WITH AVAILABLE TIME
    # ========================================================

    available_minutes = extract_available_minutes(
        text_lower
    )

    if available_minutes is not None:
        return "study_plan_with_time"


    # ========================================================
    # NEXT STUDY ACTION
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "what should i do right now",
            "what should i do now",
            "what do i do now",
            "next thing to study",
            "what should i work on right now",
            "what should i start",
            "what should i start with",
        ]
    ):
        return "next_study_action"


    # ========================================================
    # NORMAL STUDY PLANNER
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "study plan",
            "study planner",
            "what should i study",
            "what should i study today",
            "what do i study",
            "what should i work on",
            "what should i focus on",
            "plan my study",
            "make me a study plan",
            "study schedule",
            "plan my studies",
            "what should i prepare",
            "organize my study",
        ]
    ):
        return "study_planner"


    # ========================================================
    # ADD ACADEMIC TASK
    # ========================================================

    task_words = r"(assignment|quiz|lab|homework|task)"

    if (
        re.search(
            rf"\b(add|create|make|schedule|set up)\b.*\b{task_words}\b",
            text_lower,
        )
        or re.search(
            rf"\bnew\b.*\b{task_words}\b",
            text_lower,
        )
    ):
        return "add_assignment"


    # ========================================================
    # QUIZ-SPECIFIC
    # ========================================================

    if (
        "quiz" in text_lower

        and any(
            phrase in text_lower
            for phrase in [
                "show",
                "list",
                "what",
                "which",
                "my",
            ]
        )

        and not any(
            word in text_lower
            for word in [
                "add",
                "create",
                "new",
                "make",
                "schedule",
                "set up",
                "have a",
                "got a",
            ]
        )
    ):

        if "pending" in text_lower:
            return "pending_quizzes"

        if "next" in text_lower:
            return "next_quiz"

        return "get_quizzes"


    # ========================================================
    # LAB-SPECIFIC
    # ========================================================

    if (
        (
            "lab" in text_lower
            or "laboratory" in text_lower
        )

        and any(
            phrase in text_lower
            for phrase in [
                "show",
                "list",
                "what",
                "which",
                "my",
            ]
        )

        and not any(
            word in text_lower
            for word in [
                "add",
                "create",
                "new",
                "make",
                "schedule",
                "set up",
                "have a",
                "got a",
            ]
        )
    ):

        if "pending" in text_lower:
            return "pending_labs"

        if "next" in text_lower:
            return "next_lab"

        return "get_labs"


    # ========================================================
    # DUE TODAY
    # ========================================================

    if (
        "due today" in text_lower
        or (
            "today" in text_lower
            and "due" in text_lower
        )
    ):
        return "due_today"


    # ========================================================
    # DUE TOMORROW
    # ========================================================

    if (
        "due tomorrow" in text_lower
        or (
            "tomorrow" in text_lower
            and "due" in text_lower
        )
    ):
        return "due_tomorrow"


    # ========================================================
    # DUE THIS WEEK
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "due this week",
            "deadlines this week",
            "what is due this week",
            "what's due this week",
        ]
    ):
        return "due_this_week"


    # ========================================================
    # OVERDUE
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "overdue",
            "late assignments",
            "late tasks",
            "what am i late on",
        ]
    ):
        return "overdue_assignments"


    # ========================================================
    # NEXT DEADLINE
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "next deadline",
            "next due",
            "what is due next",
            "what's due next",
            "upcoming deadline",
        ]
    ):
        return "next_deadline"


    # ========================================================
    # WORK RECOMMENDATION
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "what should i work on",
            "what should i do",
            "what should i complete",
            "what should i finish",
            "recommend something",
            "recommend a task",
        ]
    ):
        return "work_recommendation"


    # ========================================================
    # COMPLETE CURRENT STUDY TASK
    # ========================================================

    # These phrases refer to the task that the study planner
    # previously recommended.
    #
    # Examples:
    # "I finished this"
    # "I finished it"
    # "I completed this"
    # "I completed it"
    # "I'm done with this"
    # "done with this"
    # "this is done"
    # "finished this"
    # "completed this"

    if any(
        phrase in text_lower
        for phrase in [
            "i finished this",
            "i finished it",
            "i completed this",
            "i completed it",
            "i'm done with this",
            "im done with this",
            "i am done with this",
            "done with this",
            "done with it",
            "this is done",
            "finished this",
            "finished it",
            "completed this",
            "completed it",
        ]
    ):
        return "complete_current_task"


    # ========================================================
    # COMPLETE SPECIFIC TASK
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "complete assignment",
            "complete task",
            "finish assignment",
            "finish task",
            "mark complete",
            "mark as complete",
            "done with assignment",
            "finished assignment",
        ]
    ):
        return "complete_assignment"


    # ========================================================
    # DELETE TASK
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "delete assignment",
            "delete task",
            "remove assignment",
            "remove task",
        ]
    ):
        return "delete_assignment"


    # ========================================================
    # GENERAL ASSIGNMENTS
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "show assignments",
            "list assignments",
            "my assignments",
            "all assignments",
            "show my assignments",
            "what assignments do i have",
        ]
    ):
        return "get_assignments"


    # ========================================================
    # PENDING TASKS
    # ========================================================

    if any(
        phrase in text_lower
        for phrase in [
            "pending assignments",
            "pending tasks",
            "what is pending",
            "what's pending",
            "unfinished assignments",
            "unfinished tasks",
        ]
    ):
        return "get_pending"


    # ========================================================
    # COURSE-SPECIFIC ASSIGNMENTS
    # ========================================================

    if (
        "assignment" in text_lower

        and any(
            phrase in text_lower
            for phrase in [
                "for",
                "in",
                "from",
            ]
        )
    ):

        course = extract_course(
            text_lower
        )

        if course:
            return "course_assignments"


    # ========================================================
    # UNKNOWN
    # ========================================================

    return "unknown"


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_tool(
    intent,
    parameters=None,
):

    if parameters is None:
        parameters = {}


    # ========================================================
    # ADD ASSIGNMENT / QUIZ / LAB
    # ========================================================

    if intent == "add_assignment":

        return add_assignment(
            course=parameters.get(
                "course"
            ),

            title=parameters.get(
                "title"
            ),

            due_date=parameters.get(
                "due_date"
            ),

            description=parameters.get(
                "description",
                "",
            ),

            task_type=parameters.get(
                "task_type",
                "assignment",
            ),
        )


    # ========================================================
    # ALL ASSIGNMENTS
    # ========================================================

    if intent == "get_assignments":

        return get_assignments()


    # ========================================================
    # PENDING ASSIGNMENTS
    # ========================================================

    if intent == "get_pending":

        return get_pending_assignments()


    # ========================================================
    # QUIZZES
    # ========================================================

    if intent == "get_quizzes":

        return get_tasks_by_type(
            "quiz"
        )


    # ========================================================
    # PENDING QUIZZES
    # ========================================================

    if intent == "pending_quizzes":

        return get_pending_tasks_by_type(
            "quiz"
        )


    # ========================================================
    # LABS
    # ========================================================

    if intent == "get_labs":

        return get_tasks_by_type(
            "lab"
        )


    # ========================================================
    # PENDING LABS
    # ========================================================

    if intent == "pending_labs":

        return get_pending_tasks_by_type(
            "lab"
        )


    # ========================================================
    # DUE TODAY
    # ========================================================

    if intent == "due_today":

        return get_due_today()


    # ========================================================
    # DUE TOMORROW
    # ========================================================

    if intent == "due_tomorrow":

        return get_due_tomorrow()


    # ========================================================
    # DUE THIS WEEK
    # ========================================================

    if intent == "due_this_week":

        return get_due_this_week()


    # ========================================================
    # OVERDUE
    # ========================================================

    if intent == "overdue_assignments":

        return get_overdue_assignments()


    # ========================================================
    # NEXT DEADLINE
    # ========================================================

    if intent == "next_deadline":

        return get_next_deadline()


    # ========================================================
    # NEXT QUIZ
    # ========================================================

    if intent == "next_quiz":

        tasks = get_pending_tasks_by_type(
            "quiz"
        )

        if not tasks:
            return "🎉 No pending quizzes."

        tasks = sorted(
            tasks,
            key=lambda task: (
                task.get(
                    "due_date",
                    "9999-12-31",
                )
            ),
        )

        return tasks[0]


    # ========================================================
    # NEXT LAB
    # ========================================================

    if intent == "next_lab":

        tasks = get_pending_tasks_by_type(
            "lab"
        )

        if not tasks:
            return "🎉 No pending labs."

        tasks = sorted(
            tasks,
            key=lambda task: (
                task.get(
                    "due_date",
                    "9999-12-31",
                )
            ),
        )

        return tasks[0]


    # ========================================================
    # WORK RECOMMENDATION
    # ========================================================

    if intent == "work_recommendation":

        return get_work_recommendations()


    # ========================================================
    # COURSE ASSIGNMENTS
    # ========================================================

    if intent == "course_assignments":

        return get_course_assignments(
            parameters.get(
                "course"
            )
        )


    # ========================================================
    # COMPLETE ASSIGNMENT
    # ========================================================

    if intent == "complete_assignment":

        return complete_assignment(
            parameters.get(
                "assignment_id"
            )
        )


    # ========================================================
    # COMPLETE CURRENT TASK
    # ========================================================

    # This intent is handled by the LangGraph node because
    # the current task ID comes from conversation state.

    if intent == "complete_current_task":

        return {
            "status": "needs_current_task"
        }


    # ========================================================
    # DELETE ASSIGNMENT
    # ========================================================

    if intent == "delete_assignment":

        return delete_assignment(
            parameters.get(
                "assignment_id"
            )
        )


    # ========================================================
    # REFRESH COURSES
    # ========================================================

    if intent == "refresh_courses":

        return refresh_courses()


    # ========================================================
    # WORKLOAD SUMMARY
    # ========================================================

    if intent == "workload_summary":

        return format_workload_summary()


    # ========================================================
    # NORMAL STUDY PLANNER
    # ========================================================

    if intent == "study_planner":

        return study_planner.invoke({})


    # ========================================================
    # STUDY PLAN WITH AVAILABLE TIME
    # ========================================================

    if intent == "study_plan_with_time":

        available_minutes = parameters.get(
            "available_minutes"
        )

        if available_minutes is None:

            return (
                "⏱️ Please tell me how much time "
                "you have.\n\n"

                "Examples:\n"
                "• I have 3 hours\n"
                "• I have 90 minutes\n"
                "• I can study for 2 hours"
            )

        return study_plan_with_time.invoke(
            {
                "available_minutes":
                    available_minutes
            }
        )


    # ========================================================
    # NEXT STUDY ACTION
    # ========================================================

    if intent == "next_study_action":

        return next_study_action.invoke({})


    # ========================================================
    # UNKNOWN
    # ========================================================

    return (
        "I couldn't understand that request."
    )