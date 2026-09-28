from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pathlib import Path
from backend.app.graph.graph import chat
from backend.app.course_service import (
    get_courses,
    get_course_details,
)
import sqlite3
from pathlib import Path
from datetime import date

from backend.app.tools.assignment_tool import (
    get_assignments,
    add_assignment,
    complete_assignment,
    delete_assignment,
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI University OS",
    description="AI-powered university assistant using LangGraph, RAG and Tools",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    course: str | None = None


class AssignmentRequest(BaseModel):
    course: str
    title: str
    due_date: str
    description: str = ""


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI University OS API is running",
        "status": "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat_endpoint(request: ChatRequest):

    try:

        response = chat(
            request.message,
            course=request.course
        )

        return {
            "response": response
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard")
def dashboard():

    db_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "university.db"
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            course,
            title,
            due_date,
            description,
            status,
            task_type
        FROM assignments
        WHERE status = 'pending'
        ORDER BY due_date ASC
    """)

    tasks = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    today = date.today().isoformat()

    pending = []
    overdue = []
    upcoming = []

    for task in tasks:

        pending.append(task)

        if task["due_date"] < today:
            overdue.append(task)

        else:
            upcoming.append(task)

    quizzes = [
        task
        for task in pending
        if task.get("task_type") == "quiz"
    ]

    labs = [
        task
        for task in pending
        if task.get("task_type") == "lab"
    ]

    assignments = [
        task
        for task in pending
        if task.get("task_type") == "assignment"
    ]

    return {

        "summary": {
            "pending": len(pending),
            "overdue": len(overdue),
            "assignments": len(assignments),
            "quizzes": len(quizzes),
            "labs": len(labs)
        },

        "overdue": overdue,

        "upcoming": upcoming[:5],

        "quizzes": quizzes[:5],

        "labs": labs[:5]
    }


# ============================================================
# ASSIGNMENTS API
# ============================================================

@app.get("/assignments")
def assignments_endpoint():

    try:

        all_tasks = get_assignments()

        assignments = [
            task
            for task in all_tasks
            if task.get("task_type", "assignment") == "assignment"
        ]

        today = date.today().isoformat()

        pending = []
        overdue = []
        completed = []

        for assignment in assignments:

            if assignment.get("status") == "completed":

                completed.append(assignment)

            elif assignment.get("status") == "pending":

                if assignment.get("due_date", "") < today:

                    overdue.append(assignment)

                else:

                    pending.append(assignment)

        return {

            "assignments": assignments,

            "pending": pending,

            "overdue": overdue,

            "completed": completed,

            "count": len(assignments),

            "summary": {
                "total": len(assignments),
                "pending": len(pending),
                "overdue": len(overdue),
                "completed": len(completed)
            }
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# ADD ASSIGNMENT
# ============================================================

@app.post("/assignments")
def add_assignment_endpoint(
    request: AssignmentRequest
):

    try:

        result = add_assignment(

            course=request.course,

            title=request.title,

            due_date=request.due_date,

            description=request.description,

            task_type="assignment",

        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# COMPLETE ASSIGNMENT
# ============================================================

@app.patch("/assignments/{assignment_id}/complete")
def complete_assignment_endpoint(
    assignment_id: int
):

    try:

        result = complete_assignment(
            assignment_id
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# DELETE ASSIGNMENT
# ============================================================

@app.delete("/assignments/{assignment_id}")
def delete_assignment_endpoint(
    assignment_id: int
):

    try:

        result = delete_assignment(
            assignment_id
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# QUIZZES API
# ============================================================

@app.get("/quizzes")
def quizzes_endpoint():

    try:

        all_tasks = get_assignments()

        quizzes = [
            task
            for task in all_tasks
            if task.get("task_type") == "quiz"
        ]

        today = date.today().isoformat()

        pending = []
        overdue = []
        completed = []

        for quiz in quizzes:

            if quiz.get("status") == "completed":

                completed.append(quiz)

            elif quiz.get("status") == "pending":

                if quiz.get("due_date", "") < today:

                    overdue.append(quiz)

                else:

                    pending.append(quiz)

        return {

            "quizzes": quizzes,

            "pending": pending,

            "overdue": overdue,

            "completed": completed,

            "count": len(quizzes),

            "summary": {
                "total": len(quizzes),
                "pending": len(pending),
                "overdue": len(overdue),
                "completed": len(completed)
            }
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# ADD QUIZ
# ============================================================

@app.post("/quizzes")
def add_quiz_endpoint(
    request: AssignmentRequest
):

    try:

        result = add_assignment(

            course=request.course,

            title=request.title,

            due_date=request.due_date,

            description=request.description,

            task_type="quiz",

        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# COMPLETE QUIZ
# ============================================================

@app.patch("/quizzes/{quiz_id}/complete")
def complete_quiz_endpoint(
    quiz_id: int
):

    try:

        result = complete_assignment(
            quiz_id
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# DELETE QUIZ
# ============================================================

@app.delete("/quizzes/{quiz_id}")
def delete_quiz_endpoint(
    quiz_id: int
):

    try:

        result = delete_assignment(
            quiz_id
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# LABS API
# ============================================================

@app.get("/labs")
def labs_endpoint():

    try:

        # Get everything from database
        all_tasks = get_assignments()

        # Only labs
        labs = [
            task
            for task in all_tasks
            if task.get("task_type") == "lab"
        ]

        today = date.today().isoformat()

        pending = []
        overdue = []
        completed = []

        for lab in labs:

            # Completed
            if lab.get("status") == "completed":

                completed.append(lab)

            # Pending
            elif lab.get("status") == "pending":

                if lab.get("due_date", "") < today:

                    overdue.append(lab)

                else:

                    pending.append(lab)

        return {

            "labs": labs,

            "pending": pending,

            "overdue": overdue,

            "completed": completed,

            "count": len(labs),

            "summary": {

                "total": len(labs),

                "pending": len(pending),

                "overdue": len(overdue),

                "completed": len(completed)

            }

        }

    except Exception as e:

        return {

            "error": str(e)

        }


# ============================================================
# ADD LAB
# ============================================================

@app.post("/labs")
def add_lab_endpoint(
    request: AssignmentRequest
):

    try:

        result = add_assignment(

            course=request.course,

            title=request.title,

            due_date=request.due_date,

            description=request.description,

            task_type="lab",

        )

        return result

    except Exception as e:

        return {

            "error": str(e)

        }


# ============================================================
# COMPLETE LAB
# ============================================================

@app.patch("/labs/{lab_id}/complete")
def complete_lab_endpoint(
    lab_id: int
):

    try:

        result = complete_assignment(
            lab_id
        )

        return result

    except Exception as e:

        return {

            "error": str(e)

        }


# ============================================================
# DELETE LAB
# ============================================================

@app.delete("/labs/{lab_id}")
def delete_lab_endpoint(
    lab_id: int
):

    try:

        result = delete_assignment(
            lab_id
        )

        return result

    except Exception as e:

        return {

            "error": str(e)

        }
@app.get("/courses")
def courses():

    return get_courses()
@app.get("/courses/{course_code}")
def course_details(course_code: str):

    course = get_course_details(
        course_code
    )

    if course is None:

        return {
            "error": "Course not found"
        }

    return course
# =========================================================
# OPEN LECTURE FILE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LECTURES_ROOT = PROJECT_ROOT / "data" / "lectures"


@app.get("/lectures/file")
def open_lecture_file(path: str):

    try:
        # Convert Windows path to a proper Path
        relative_path = Path(path)

        # Only allow files inside data/lectures
        file_path = (PROJECT_ROOT / relative_path).resolve()
        lectures_root = LECTURES_ROOT.resolve()

        # Security check
        if not file_path.is_relative_to(lectures_root):
            raise HTTPException(
                status_code=403,
                detail="Access to this file is not allowed."
            )

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Lecture file not found."
            )

        if not file_path.is_file():
            raise HTTPException(
                status_code=400,
                detail="Requested path is not a file."
            )

        # PDF → browser mein open
        if file_path.suffix.lower() == ".pdf":

            return FileResponse(
                path=str(file_path),
                media_type="application/pdf",
                content_disposition_type="inline",
                filename=file_path.name
            )

        # Other files → download
        return FileResponse(
            path=str(file_path),
            filename=file_path.name
        )

    except HTTPException:
        raise

    except Exception as error:

        print("Lecture file error:", error)

        raise HTTPException(
            status_code=500,
            detail="Could not open lecture file."
        )
