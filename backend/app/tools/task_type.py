def detect_task_type(text):
    """
    Detect the type of academic task.

    Supported:
    - assignment
    - quiz
    - lab
    """

    text = text.lower().strip()

    # Quiz
    quiz_words = [
        "quiz",
        "quizz",
        "mcq",
        "mcqs",
        "test"
    ]

    if any(word in text for word in quiz_words):
        return "quiz"

    # Lab
    lab_words = [
        "lab",
        "laboratory",
        "lab task",
        "lab work",
        "practical"
    ]

    if any(word in text for word in lab_words):
        return "lab"

    # Assignment
    assignment_words = [
        "assignment",
        "homework",
        "task"
    ]

    if any(word in text for word in assignment_words):
        return "assignment"

    return "assignment"


def format_task_type(task_type):
    """
    Return a friendly label for the task type.
    """

    labels = {
        "assignment": "📘 Assignment",
        "quiz": "📝 Quiz",
        "lab": "🧪 Lab"
    }

    return labels.get(
        str(task_type).lower(),
        "📌 Task"
    )
