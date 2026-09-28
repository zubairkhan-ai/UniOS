from datetime import date, timedelta

from langchain_core.tools import tool

from .assignment_tool import (
    get_assignments,
    get_pending_assignments,
    get_tasks_by_type,
    get_pending_tasks_by_type
)


# ============================================================
# DATE
# ============================================================

def get_today():
    return date.today()


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


# ============================================================
# FORMATTING
# ============================================================

def format_task(task):
    """
    Format one academic task.
    """

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

    label = task_type.capitalize()

    return (
        f"[{task['id']}] "
        f"{icon} "
        f"{task['course']} - "
        f"{task['title']} "
        f"| Type: {label} "
        f"| Due: {task['due_date']} "
        f"| Status: {task['status']}"
    )


def format_tasks(tasks):

    if not tasks:
        return "No assignments found."

    return "\n".join(
        format_task(task)
        for task in tasks
    )


# ============================================================
# DUE TODAY
# ============================================================

def get_due_today():

    today = get_today().isoformat()

    tasks = [
        task
        for task in get_assignments()
        if task["due_date"] == today
        and task["status"] == "pending"
    ]

    return tasks


# ============================================================
# DUE TOMORROW
# ============================================================

def get_due_tomorrow():

    tomorrow = (
        get_today() + timedelta(days=1)
    ).isoformat()

    tasks = [
        task
        for task in get_assignments()
        if task["due_date"] == tomorrow
        and task["status"] == "pending"
    ]

    return tasks


# ============================================================
# DUE THIS WEEK
# ============================================================

def get_due_this_week():

    today = get_today()

    # Monday = 0
    week_end = today + timedelta(
        days=6 - today.weekday()
    )

    tasks = []

    for task in get_assignments():

        due = parse_date(
            task["due_date"]
        )

        if not due:
            continue

        if (
            today <= due <= week_end
            and task["status"] == "pending"
        ):
            tasks.append(task)

    return tasks


# ============================================================
# OVERDUE
# ============================================================

def get_overdue_assignments():

    today = get_today()

    tasks = []

    for task in get_assignments():

        due = parse_date(
            task["due_date"]
        )

        if not due:
            continue

        if (
            due < today
            and task["status"] == "pending"
        ):
            tasks.append(task)

    return tasks


# ============================================================
# NEXT DEADLINE
# ============================================================

def get_next_deadline():

    today = get_today()

    pending = get_pending_assignments()

    upcoming = []

    for task in pending:

        due = parse_date(
            task["due_date"]
        )

        if not due:
            continue

        if due >= today:
            upcoming.append(task)

    if not upcoming:
        return None

    upcoming.sort(
        key=lambda task: task["due_date"]
    )

    return upcoming[0]


# ============================================================
# COURSE TASKS
# ============================================================

def get_course_assignments(course):

    tasks = [
        task
        for task in get_assignments()
        if task["course"].lower() == course.lower()
    ]

    return tasks


# ============================================================
# TASK TYPE
# ============================================================

def get_type_tasks(task_type):

    return get_tasks_by_type(task_type)


# ============================================================
# WORK RECOMMENDATIONS
# ============================================================

def get_work_recommendations():

    today = get_today()

    pending = get_pending_assignments()

    valid_tasks = []

    for task in pending:

        due = parse_date(
            task["due_date"]
        )

        if not due:
            continue

        days_remaining = (
            due - today
        ).days

        task_copy = dict(task)

        task_copy["days_remaining"] = (
            days_remaining
        )

        valid_tasks.append(task_copy)

    valid_tasks.sort(
        key=lambda task: (
            task["days_remaining"],
            task["due_date"]
        )
    )

    return valid_tasks


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

@tool
def due_today_tool():
    """Get all pending academic tasks due today."""
    
    tasks = get_due_today()

    return format_tasks(tasks)


@tool
def due_tomorrow_tool():
    """Get all pending academic tasks due tomorrow."""
    
    tasks = get_due_tomorrow()

    return format_tasks(tasks)


@tool
def due_this_week_tool():
    """Get all pending academic tasks due during the current week."""
    
    tasks = get_due_this_week()

    return format_tasks(tasks)


@tool
def overdue_assignments_tool():
    """Get all pending academic tasks whose due date has passed."""
    
    tasks = get_overdue_assignments()

    return format_tasks(tasks)


@tool
def next_deadline_tool():
    """Get the next upcoming pending academic task."""
    
    task = get_next_deadline()

    if not task:
        return "No upcoming deadlines."

    return task


@tool
def course_assignments_tool(course: str):
    """Get all academic tasks for a specific course."""
    
    tasks = get_course_assignments(course)

    return format_tasks(tasks)


@tool
def work_recommendation_tool():
    """Get pending academic tasks ordered by their upcoming deadlines."""
    
    tasks = get_work_recommendations()

    if not tasks:
        return "No pending work."

    return tasks


@tool
def quiz_tool():
    """Get all quizzes."""
    
    return format_tasks(
        get_tasks_by_type("quiz")
    )


@tool
def pending_quiz_tool():
    """Get all pending quizzes."""
    
    return format_tasks(
        get_pending_tasks_by_type("quiz")
    )


@tool
def lab_tool():
    """Get all lab tasks."""
    
    return format_tasks(
        get_tasks_by_type("lab")
    )


@tool
def pending_lab_tool():
    """Get all pending lab tasks."""
    
    return format_tasks(
        get_pending_tasks_by_type("lab")
    )