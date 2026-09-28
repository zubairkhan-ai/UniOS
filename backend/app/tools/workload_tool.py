from datetime import date

from .assignment_tool import (
    get_assignments,
    get_pending_assignments,
    get_tasks_by_type,
    get_pending_tasks_by_type
)

from .deadline_tool import (
    get_overdue_assignments,
    get_due_today,
    get_due_tomorrow,
    get_due_this_week,
    get_next_deadline
)


# ============================================================
# WORKLOAD SUMMARY
# ============================================================

def get_workload_summary():

    all_tasks = get_assignments()
    pending = get_pending_assignments()

    assignments = [
        task
        for task in all_tasks
        if task.get("task_type", "assignment").lower()
        == "assignment"
    ]

    quizzes = [
        task
        for task in all_tasks
        if task.get("task_type", "assignment").lower()
        == "quiz"
    ]

    labs = [
        task
        for task in all_tasks
        if task.get("task_type", "assignment").lower()
        == "lab"
    ]

    pending_assignments = [
        task
        for task in pending
        if task.get("task_type", "assignment").lower()
        == "assignment"
    ]

    pending_quizzes = [
        task
        for task in pending
        if task.get("task_type", "assignment").lower()
        == "quiz"
    ]

    pending_labs = [
        task
        for task in pending
        if task.get("task_type", "assignment").lower()
        == "lab"
    ]

    return {
        "total": len(all_tasks),

        "pending": len(pending),

        "completed": (
            len(all_tasks) -
            len(pending)
        ),

        "assignments": len(assignments),
        "pending_assignments": len(
            pending_assignments
        ),

        "quizzes": len(quizzes),
        "pending_quizzes": len(
            pending_quizzes
        ),

        "labs": len(labs),
        "pending_labs": len(
            pending_labs
        ),

        "overdue": len(
            get_overdue_assignments()
        ),

        "due_today": len(
            get_due_today()
        ),

        "due_tomorrow": len(
            get_due_tomorrow()
        ),

        "due_this_week": len(
            get_due_this_week()
        ),

        "next_deadline": get_next_deadline()
    }


# ============================================================
# FORMAT
# ============================================================

def format_workload_summary():

    summary = get_workload_summary()

    result = []

    result.append("📊 ACADEMIC WORKLOAD")
    result.append("")
    
    result.append(
        f"Total academic tasks: "
        f"{summary['total']}"
    )

    result.append(
        f"Pending: {summary['pending']}"
    )

    result.append(
        f"Completed: {summary['completed']}"
    )

    result.append(
        f"Overdue: {summary['overdue']}"
    )

    result.append("")

    result.append("📘 ASSIGNMENTS")
    result.append(
        f"Total: {summary['assignments']}"
    )
    result.append(
        f"Pending: {summary['pending_assignments']}"
    )

    result.append("")

    result.append("📝 QUIZZES")
    result.append(
        f"Total: {summary['quizzes']}"
    )
    result.append(
        f"Pending: {summary['pending_quizzes']}"
    )

    result.append("")

    result.append("🧪 LAB TASKS")
    result.append(
        f"Total: {summary['labs']}"
    )
    result.append(
        f"Pending: {summary['pending_labs']}"
    )

    result.append("")

    result.append("📅 DEADLINES")
    result.append(
        f"Due today: {summary['due_today']}"
    )
    result.append(
        f"Due tomorrow: {summary['due_tomorrow']}"
    )
    result.append(
        f"Due this week: {summary['due_this_week']}"
    )

    next_deadline = summary["next_deadline"]

    if next_deadline:

        result.append("")
        result.append("⏰ NEXT DEADLINE")

        task_type = next_deadline.get(
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

        result.append(
            f"{icon} "
            f"{next_deadline['course']} - "
            f"{next_deadline['title']}"
        )

        result.append(
            f"Due: {next_deadline['due_date']}"
        )

        result.append(
            f"Status: {next_deadline['status']}"
        )

    else:

        result.append("")
        result.append(
            "🎉 No upcoming deadlines."
        )

    return "\n".join(result)