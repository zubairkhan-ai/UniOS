from pathlib import Path
from datetime import datetime
import sqlite3
import re

from langchain_core.tools import tool


# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATABASE_PATH = BACKEND_DIR / "data" / "university.db"
LECTURES_DIR = PROJECT_ROOT / "data" / "lectures"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a connection to the university database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Create required tables and migrate old databases.

    Existing assignment data is NOT deleted.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # Courses table
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            semester TEXT
        )
        """
    )

    # --------------------------------------------------------
    # Assignments / academic tasks table
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
        """
    )

    # --------------------------------------------------------
    # Migration:
    # Add task_type to old databases
    # --------------------------------------------------------

    cursor.execute("PRAGMA table_info(assignments)")

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "task_type" not in columns:
        cursor.execute(
            """
            ALTER TABLE assignments
            ADD COLUMN task_type TEXT DEFAULT 'assignment'
            """
        )

    connection.commit()
    connection.close()


# Initialize database when module loads
initialize_database()


# ============================================================
# ADD TASK
# ============================================================

def add_assignment(
    course,
    title,
    due_date,
    description="",
    task_type="assignment"
):
    """
    Add an academic task.

    task_type can be:
        assignment
        quiz
        lab
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO assignments
        (
            course,
            title,
            description,
            due_date,
            status,
            task_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            course,
            title,
            description,
            due_date,
            "pending",
            task_type,
            created_at
        )
    )

    assignment_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "success": True,
        "id": assignment_id,
        "course": course,
        "title": title,
        "description": description,
        "due_date": due_date,
        "status": "pending",
        "task_type": task_type
    }


# ============================================================
# GET ALL TASKS
# ============================================================

def get_assignments():
    """
    Return all academic tasks.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM assignments
        ORDER BY due_date ASC, id ASC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# GET PENDING TASKS
# ============================================================

def get_pending_assignments():
    """
    Return all pending academic tasks.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM assignments
        WHERE status = 'pending'
        ORDER BY due_date ASC, id ASC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# GET TASKS BY TYPE
# ============================================================

def get_tasks_by_type(task_type):
    """
    Return tasks of a specific type.

    Example:
        assignment
        quiz
        lab
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM assignments
        WHERE LOWER(task_type) = LOWER(?)
        ORDER BY due_date ASC, id ASC
        """,
        (task_type,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# GET PENDING TASKS BY TYPE
# ============================================================

def get_pending_tasks_by_type(task_type):
    """
    Return pending tasks of a specific type.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM assignments
        WHERE LOWER(task_type) = LOWER(?)
        AND status = 'pending'
        ORDER BY due_date ASC, id ASC
        """,
        (task_type,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# COMPLETE TASK
# ============================================================

def complete_assignment(assignment_id):
    """
    Mark a task as completed.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE assignments
        SET status = 'completed'
        WHERE id = ?
        """,
        (assignment_id,)
    )

    changed = cursor.rowcount

    connection.commit()
    connection.close()

    if changed == 0:
        return {
            "success": False,
            "message": f"No task found with ID {assignment_id}."
        }

    return {
        "success": True,
        "message": f"Task {assignment_id} marked as completed."
    }


# ============================================================
# DELETE TASK
# ============================================================

def delete_assignment(assignment_id):
    """
    Delete an academic task.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM assignments
        WHERE id = ?
        """,
        (assignment_id,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted == 0:
        return {
            "success": False,
            "message": f"No task found with ID {assignment_id}."
        }

    return {
        "success": True,
        "message": f"Task {assignment_id} deleted successfully."
    }


# ============================================================
# COURSE FUNCTIONS
# ============================================================

def add_course(code, name, semester=""):
    """
    Add a course if it does not already exist.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO courses
            (code, name, semester)
            VALUES (?, ?, ?)
            """,
            (code, name, semester)
        )

        connection.commit()

        course_id = cursor.lastrowid

        connection.close()

        return {
            "success": True,
            "id": course_id,
            "code": code,
            "name": name
        }

    except sqlite3.IntegrityError:

        connection.close()

        return {
            "success": False,
            "message": f"Course {code} already exists."
        }


def get_courses():
    """
    Return all courses.
    """

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM courses
        ORDER BY code
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# COURSE FINDER
# ============================================================

def find_course(course_text):
    """
    Find a course from its code/name.
    """

    if not course_text:
        return None

    search = course_text.lower().strip()

    courses = get_courses()

    # Exact code match
    for course in courses:
        if course["code"].lower() == search:
            return course

    # Name match
    for course in courses:
        if course["name"].lower() == search:
            return course

    # Partial code/name match
    for course in courses:
        if search in course["code"].lower():
            return course

        if search in course["name"].lower():
            return course

    return None


# ============================================================
# COURSE DISCOVERY
# ============================================================

COURSE_MAP = {
    "os": ("OS", "Operating Systems"),
    "operating systems": ("OS", "Operating Systems"),

    "daa": (
        "DAA",
        "Design and Analysis of Algorithms"
    ),
    "design and analysis of algorithms": (
        "DAA",
        "Design and Analysis of Algorithms"
    ),

    "cn": ("CN", "Computer Networks"),
    "computer networks": (
        "CN",
        "Computer Networks"
    ),

    "coal": (
        "COAL",
        "Computer Organization and Assembly Language"
    ),
    "computer organization and assembly language": (
        "COAL",
        "Computer Organization and Assembly Language"
    ),

    "krr": (
        "KRR",
        "Knowledge Representation and Reasoning"
    ),
    "knowledge representation and reasoning": (
        "KRR",
        "Knowledge Representation and Reasoning"
    ),

    "rl": (
        "RL",
        "Reinforcement Learning"
    ),
    "reinforcement learning": (
        "RL",
        "Reinforcement Learning"
    ),

    "cv": (
        "CV",
        "Computer Vision"
    ),
    "computer vision": (
        "CV",
        "Computer Vision"
    ),

    "nlp": (
        "NLP",
        "Natural Language Processing"
    ),
    "natural language processing": (
        "NLP",
        "Natural Language Processing"
    ),

    "db": (
        "DB",
        "Database Systems"
    ),
    "database systems": (
        "DB",
        "Database Systems"
    ),

    "ann": (
        "ANN",
        "Artificial Neural Networks"
    ),
    "artificial neural networks": (
        "ANN",
        "Artificial Neural Networks"
    ),

    "ml": (
        "ML",
        "Machine Learning"
    ),
    "machine learning": (
        "ML",
        "Machine Learning"
    ),

    "bigdata": (
        "BIGDATA",
        "Big Data"
    ),
    "big data": (
        "BIGDATA",
        "Big Data"
    ),

    "web and ai": (
        "WEB_AI",
        "Web and AI"
    ),
    "web_ai": (
        "WEB_AI",
        "Web and AI"
    ),

    "oop": (
        "OOP",
        "Object Oriented Programming"
    ),
    "opp": (
        "OOP",
        "Object Oriented Programming"
    ),
    "object oriented programming": (
        "OOP",
        "Object Oriented Programming"
    ),
    "object-oriented programming": (
        "OOP",
        "Object Oriented Programming"
    )
}


def discover_courses_from_lectures():
    """
    Discover courses from lecture folder names.
    """

    if not LECTURES_DIR.exists():
        return []

    found_courses = []

    for item in LECTURES_DIR.iterdir():

        if not item.is_dir():
            continue

        folder_name = item.name.strip()
        normalized = folder_name.lower()

        if normalized in COURSE_MAP:

            code, name = COURSE_MAP[normalized]

        else:

            # Generic initials
            words = re.findall(
                r"[A-Za-z]+",
                folder_name
            )

            meaningful_words = [
                word
                for word in words
                if word.lower() != "and"
            ]

            if not meaningful_words:
                continue

            code = "".join(
                word[0]
                for word in meaningful_words
            ).upper()

            name = folder_name

        found_courses.append(
            {
                "code": code,
                "name": name
            }
        )

    return found_courses


def sync_courses_from_lectures():
    """
    Add discovered courses to the database.
    """

    discovered = discover_courses_from_lectures()

    added = []

    for course in discovered:

        existing = find_course(course["code"])

        if existing:
            continue

        result = add_course(
            course["code"],
            course["name"]
        )

        if result.get("success"):
            added.append(course)

    return added


def refresh_courses():
    """
    Rescan lecture folders and add missing courses.
    """

    added = sync_courses_from_lectures()

    return {
        "success": True,
        "message": (
            f"Course refresh complete. "
            f"Added {len(added)} new course(s)."
        ),
        "added": added,
        "courses": get_courses()
    }


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

@tool
def add_assignment_tool(
    course: str,
    title: str,
    due_date: str,
    description: str = "",
    task_type: str = "assignment"
):
    """
    Add an assignment, quiz, or lab task.
    """

    return add_assignment(
        course=course,
        title=title,
        due_date=due_date,
        description=description,
        task_type=task_type
    )


@tool
def get_assignments_tool():
    """
    Get all academic tasks.
    """

    return get_assignments()


@tool
def get_pending_assignments_tool():
    """
    Get all pending academic tasks.
    """

    return get_pending_assignments()


@tool
def get_quizzes_tool():
    """
    Get all quizzes.
    """

    return get_tasks_by_type("quiz")


@tool
def get_pending_quizzes_tool():
    """
    Get pending quizzes.
    """

    return get_pending_tasks_by_type("quiz")


@tool
def get_labs_tool():
    """
    Get all lab tasks.
    """

    return get_tasks_by_type("lab")


@tool
def get_pending_labs_tool():
    """
    Get pending lab tasks.
    """

    return get_pending_tasks_by_type("lab")


@tool
def complete_assignment_tool(assignment_id: int):
    """
    Complete an academic task.
    """

    return complete_assignment(assignment_id)


@tool
def delete_assignment_tool(assignment_id: int):
    """
    Delete an academic task.
    """

    return delete_assignment(assignment_id)


@tool
def get_courses_tool():
    """
    Get all courses.
    """

    return get_courses()


@tool
def refresh_courses_tool():
    """
    Refresh courses from lecture folders.
    """

    return refresh_courses()