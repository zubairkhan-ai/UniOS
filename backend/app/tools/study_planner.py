from datetime import date, datetime
from collections import defaultdict

from langchain_core.tools import tool

from .assignment_tool import get_pending_assignments


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_DAILY_MINUTES = 180

BREAK_MINUTES = 10

MAX_TASKS_PER_PLAN = 6


# ============================================================
# DATE HELPERS
# ============================================================

def parse_due_date(due_date):
    """
    Convert YYYY-MM-DD into a date object.
    """

    if not due_date:
        return None

    try:
        return datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return None


def days_until_due(task):
    """
    Return number of days remaining until
    the task deadline.
    """

    due = parse_due_date(
        task.get("due_date")
    )

    if due is None:
        return None

    return (
        due - date.today()
    ).days


# ============================================================
# PRIORITY ENGINE
# ============================================================

def calculate_priority(task):
    """
    Calculate task priority from deadline
    and task type.

    Score:
        1 - 10
    """

    days_left = days_until_due(
        task
    )

    task_type = (
        task.get(
            "task_type",
            "assignment"
        )
        .lower()
    )

    score = 1

    # --------------------------------------------------------
    # DEADLINE URGENCY
    # --------------------------------------------------------

    if days_left is None:

        score += 1

    elif days_left < 0:

        # Overdue
        score += 9

    elif days_left == 0:

        # Due today
        score += 8

    elif days_left == 1:

        # Due tomorrow
        score += 7

    elif days_left <= 3:

        # Due within 3 days
        score += 5

    elif days_left <= 7:

        # Due within a week
        score += 3

    else:

        score += 1

    # --------------------------------------------------------
    # TASK TYPE
    # --------------------------------------------------------

    if task_type == "quiz":

        score += 1

    elif task_type == "lab":

        score += 2

    elif task_type == "assignment":

        score += 1

    # Keep score between 1 and 10
    return min(score, 10)


def priority_label(score):

    if score >= 9:
        return "🔴 CRITICAL"

    if score >= 7:
        return "🔴 HIGH"

    if score >= 5:
        return "🟠 MEDIUM"

    if score >= 3:
        return "🟡 LOW"

    return "🟢 VERY LOW"


# ============================================================
# STUDY TIME ENGINE
# ============================================================

def suggested_time(task):
    """
    Decide how much study time the task should receive.
    """

    task_type = (
        task.get(
            "task_type",
            "assignment"
        )
        .lower()
    )

    priority = calculate_priority(
        task
    )

    # --------------------------------------------------------
    # QUIZ
    # --------------------------------------------------------

    if task_type == "quiz":

        if priority >= 9:
            return 90

        if priority >= 7:
            return 60

        return 45

    # --------------------------------------------------------
    # LAB
    # --------------------------------------------------------

    if task_type == "lab":

        if priority >= 9:
            return 120

        if priority >= 7:
            return 90

        return 60

    # --------------------------------------------------------
    # ASSIGNMENT
    # --------------------------------------------------------

    if priority >= 9:
        return 120

    if priority >= 7:
        return 90

    if priority >= 5:
        return 60

    return 45


# ============================================================
# COURSE BALANCING
# ============================================================

def balance_courses(tasks):
    """
    Prevent the planner from selecting too many
    tasks from the same course when possible.
    """

    selected = []

    course_count = defaultdict(int)

    for task in tasks:

        course = (
            task.get(
                "course",
                "Unknown"
            )
            .upper()
        )

        # Allow at most two tasks from
        # the same course initially.
        if course_count[course] >= 2:
            continue

        selected.append(task)

        course_count[course] += 1

    # --------------------------------------------------------
    # FILL REMAINING SLOTS
    # --------------------------------------------------------

    target = min(
        MAX_TASKS_PER_PLAN,
        len(tasks)
    )

    if len(selected) < target:

        for task in tasks:

            if task not in selected:

                selected.append(task)

            if len(selected) >= target:
                break

    return selected[:MAX_TASKS_PER_PLAN]


# ============================================================
# TASK SORTING
# ============================================================

def sort_tasks(tasks):
    """
    Sort tasks by:

    1. Priority
    2. Deadline
    """

    return sorted(
        tasks,
        key=lambda task: (
            -calculate_priority(task),

            days_until_due(task)
            if days_until_due(task) is not None
            else 9999
        )
    )


# ============================================================
# SESSION GENERATOR
# ============================================================

def build_sessions(
    tasks,
    available_minutes=DEFAULT_DAILY_MINUTES
):
    """
    Convert tasks into study sessions that fit
    inside the available study time.
    """

    sessions = []

    remaining = available_minutes

    for task in tasks:

        if remaining <= 0:
            break

        required = suggested_time(
            task
        )

        session_time = min(
            required,
            remaining
        )

        # Don't create extremely
        # small sessions.
        if session_time < 15:
            break

        sessions.append(
            {
                "task": task,
                "minutes": session_time
            }
        )

        remaining -= session_time

    return sessions


# ============================================================
# TIME FORMATTING
# ============================================================

def format_duration(minutes):

    hours = minutes // 60

    mins = minutes % 60

    if hours and mins:

        return f"{hours}h {mins}m"

    if hours:

        return f"{hours}h"

    return f"{mins}m"


def format_clock(minutes):

    hours = minutes // 60

    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


# ============================================================
# DEADLINE DESCRIPTION
# ============================================================

def deadline_text(task):

    days_left = days_until_due(
        task
    )

    due_date = task.get(
        "due_date",
        "Unknown"
    )

    if days_left is None:

        return (
            f"Due: {due_date}"
        )

    if days_left < 0:

        return (
            f"⚠️ OVERDUE by "
            f"{abs(days_left)} day(s)"
        )

    if days_left == 0:

        return "🚨 Due TODAY"

    if days_left == 1:

        return "⚠️ Due TOMORROW"

    return (
        f"Due: {due_date} "
        f"({days_left} days)"
    )


# ============================================================
# DAILY STUDY PLAN
# ============================================================

def create_daily_plan(
    available_minutes=DEFAULT_DAILY_MINUTES
):
    """
    Create an intelligent daily study plan
    based on pending academic tasks.
    """

    tasks = get_pending_assignments()

    # --------------------------------------------------------
    # NO TASKS
    # --------------------------------------------------------

    if not tasks:

        return (
            "🎉 You have no pending academic tasks.\n\n"
            "Use this time for revision, projects, "
            "or skill development."
        )

    # --------------------------------------------------------
    # SORT BY PRIORITY
    # --------------------------------------------------------

    tasks = sort_tasks(
        tasks
    )

    # --------------------------------------------------------
    # BALANCE COURSES
    # --------------------------------------------------------

    tasks = balance_courses(
        tasks
    )

    # --------------------------------------------------------
    # BUILD STUDY SESSIONS
    # --------------------------------------------------------

    sessions = build_sessions(
        tasks,
        available_minutes
    )

    if not sessions:

        return (
            "⚠️ I couldn't create a useful "
            "study session with the available time."
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    lines = []

    lines.append(
        "╔══════════════════════════════════════╗"
    )

    lines.append(
        "║       🎓 YOUR STUDY COMMAND CENTER   ║"
    )

    lines.append(
        "╚══════════════════════════════════════╝"
    )

    lines.append("")

    lines.append(
        f"📅 {date.today().strftime('%d %B %Y')}"
    )

    lines.append("")

    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    # Start at 9:00 AM
    current_minutes = 9 * 60

    total_study = 0

    # --------------------------------------------------------
    # SESSIONS
    # --------------------------------------------------------

    for index, session in enumerate(
        sessions,
        start=1
    ):

        task = session["task"]

        minutes = session["minutes"]

        priority = calculate_priority(
            task
        )

        label = priority_label(
            priority
        )

        course = task.get(
            "course",
            "Unknown"
        )

        title = task.get(
            "title",
            "Untitled"
        )

        task_type = task.get(
            "task_type",
            "assignment"
        ).capitalize()

        start = format_clock(
            current_minutes
        )

        end = format_clock(
            current_minutes + minutes
        )

        lines.append("")

        lines.append(
            f"🎯 SESSION {index}"
        )

        lines.append(
            f"{start} → {end}"
        )

        lines.append(
            f"{label}"
        )

        lines.append(
            f"{course} — {title}"
        )

        lines.append(
            f"Type: {task_type}"
        )

        lines.append(
            f"⏱ {format_duration(minutes)}"
        )

        lines.append(
            deadline_text(task)
        )

        current_minutes += minutes

        total_study += minutes

        # ----------------------------------------------------
        # BREAK
        # ----------------------------------------------------

        if index < len(sessions):

            lines.append("")

            lines.append(
                f"☕ Break — {BREAK_MINUTES} minutes"
            )

            current_minutes += BREAK_MINUTES

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    lines.append("")

    lines.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    lines.append("")

    lines.append(
        "📊 TODAY'S LOAD"
    )

    lines.append(
        f"Study time: "
        f"{format_duration(total_study)}"
    )

    lines.append(
        f"Available: "
        f"{format_duration(available_minutes)}"
    )

    lines.append(
        f"Tasks: {len(sessions)}"
    )

    courses = {
        session["task"]
        .get(
            "course",
            "Unknown"
        )
        .upper()
        for session in sessions
    }

    lines.append(
        f"Courses: {len(courses)}"
    )

    lines.append("")

    lines.append(
        "💡 Start with the first session."
    )

    lines.append(
        "When you finish, tell me:"
    )

    lines.append(
        '👉 "I finished this"'
    )

    return "\n".join(
        lines
    )


# ============================================================
# NEXT STUDY ACTION
# ============================================================

def get_next_action():
    """
    Decide which task the student should work
    on next.
    """

    tasks = get_pending_assignments()

    if not tasks:

        return (
            "🎉 Nothing is pending right now.\n"
            "This is a good time for revision."
        )

    # Sort tasks
    tasks = sort_tasks(
        tasks
    )

    task = tasks[0]

    priority = calculate_priority(
        task
    )

    minutes = suggested_time(
        task
    )

    course = task.get(
        "course",
        "Unknown"
    )

    title = task.get(
        "title",
        "Untitled"
    )

    return (
        "🎯 YOUR NEXT ACTION\n\n"

        f"{priority_label(priority)}\n"

        f"{course} — {title}\n\n"

        f"⏱ Suggested session: "
        f"{format_duration(minutes)}\n"

        f"{deadline_text(task)}\n\n"

        "💡 Start this task before moving "
        "to lower-priority work."
    )


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

@tool
def study_planner():
    """
    Create today's intelligent study plan using
    pending academic tasks, deadlines, task types,
    course balancing, and available study time.
    """

    return create_daily_plan()


@tool
def study_plan_with_time(
    available_minutes: int
):
    """
    Create a study plan that fits the student's
    available number of minutes.
    """

    return create_daily_plan(
        available_minutes
    )


@tool
def next_study_action():
    """
    Decide which academic task the student
    should work on next.
    """

    return get_next_action()


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def create_study_plan():
    """
    Backward-compatible wrapper for the
    previous study planner API.

    Older code and tests can continue using:

        create_study_plan()
    """

    return create_daily_plan()