import re
from datetime import datetime, timedelta

from .assignment_tool import get_courses
from .task_type import detect_task_type


# ============================================================
# COURSE
# ============================================================

def extract_course(text):
    """
    Extract a course code/name from user input.
    """

    text_lower = text.lower()

    aliases = {
        "opp": "OOP",
        "oop": "OOP",
        "object oriented programming": "OOP",
        "object-oriented programming": "OOP",

        "os": "OS",
        "operating systems": "OS",

        "cn": "CN",
        "computer networks": "CN",

        "daa": "DAA",
        "design and analysis of algorithms": "DAA",

        "coal": "COAL",
        "computer organization": "COAL",

        "krr": "KRR",
        "knowledge representation": "KRR",

        "rl": "RL",
        "reinforcement learning": "RL",

        "cv": "CV",
        "computer vision": "CV",

        "nlp": "NLP",
        "natural language processing": "NLP",

        "db": "DB",
        "database": "DB",

        "ann": "ANN",
        "artificial neural networks": "ANN",

        "ml": "ML",
        "machine learning": "ML",

        "bigdata": "BIGDATA",
        "big data": "BIGDATA",

        "web and ai": "WEB_AI",
        "web_ai": "WEB_AI"
    }

    # Explicit alias matching
    for alias, code in aliases.items():

        if alias in text_lower:
            return code

    # Match against database courses
    courses = get_courses()

    for course in courses:

        code = course["code"]
        name = course["name"]

        if code.lower() in text_lower:
            return code

        if name.lower() in text_lower:
            return code

    return None


# ============================================================
# TITLE
# ============================================================

def extract_title(text):
    """
    Extract an explicit task title.
    """

    patterns = [
        r"(?:called|named|titled)\s+(.+?)(?:\s+(?:due|on|tomorrow|today|for)\b|$)",
        r"(?:assignment|quiz|lab|task|homework)\s+(?:called|named|titled)\s+(.+)$"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            title = match.group(1).strip()

            if title:
                return title

    text_lower = text.lower()

    if "quiz" in text_lower:
        return "Quiz"

    if "lab" in text_lower:
        return "Lab Task"

    if "homework" in text_lower:
        return "Homework"

    if "assignment" in text_lower:
        return "Assignment"

    if "task" in text_lower:
        return "Task"

    return None


# ============================================================
# TASK TYPE
# ============================================================

def extract_task_type(text):
    return detect_task_type(text)


# ============================================================
# DUE DATE
# ============================================================

def extract_due_date(text):
    """
    Extract due date from natural language.

    Supported examples:

    September 28
    October 5
    November 9
    09 November
    09 November 2026
    November 9 2026
    09/11/2026
    today
    tomorrow
    in 7 days
    """

    text_lower = text.lower().strip()

    today = datetime.now().date()

    # --------------------------------------------------------
    # Today
    # --------------------------------------------------------

    if re.search(r"\btoday\b", text_lower):
        return today.isoformat()

    # --------------------------------------------------------
    # Tomorrow
    # --------------------------------------------------------

    if re.search(r"\btomorrow\b", text_lower):
        return (
            today + timedelta(days=1)
        ).isoformat()

    # --------------------------------------------------------
    # In X days
    # --------------------------------------------------------

    match = re.search(
        r"\bin\s+(\d+)\s+days?\b",
        text_lower
    )

    if match:

        days = int(match.group(1))

        return (
            today + timedelta(days=days)
        ).isoformat()

    # --------------------------------------------------------
    # YYYY-MM-DD
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
        text
    )

    if match:

        year, month, day = map(
            int,
            match.groups()
        )

        try:
            return datetime(
                year,
                month,
                day
            ).date().isoformat()

        except ValueError:
            pass

    # --------------------------------------------------------
    # MM/DD/YYYY or MM-DD-YYYY
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",
        text
    )

    if match:

        month, day, year = map(
            int,
            match.groups()
        )

        try:
            return datetime(
                year,
                month,
                day
            ).date().isoformat()

        except ValueError:
            pass

    # --------------------------------------------------------
    # Month names
    # --------------------------------------------------------

    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }

    month_pattern = (
        r"(january|february|march|april|may|june|"
        r"july|august|september|october|november|december)"
    )

    # September 28 2026
    match = re.search(
        month_pattern +
        r"\s+(\d{1,2})(?:st|nd|rd|th)?"
        r"(?:,?\s+(\d{4}))?",
        text_lower
    )

    if match:

        month_name = match.group(1)
        day = int(match.group(2))
        year = match.group(3)

        month = months[month_name]

        if year:
            year = int(year)
        else:
            year = today.year

        try:
            result = datetime(
                year,
                month,
                day
            ).date()

            return result.isoformat()

        except ValueError:
            pass

    # 09 November 2026
    match = re.search(
        r"(\d{1,2})(?:st|nd|rd|th)?\s+"
        + month_pattern +
        r"(?:\s+(\d{4}))?",
        text_lower
    )

    if match:

        day = int(match.group(1))
        month_name = match.group(2)
        year = match.group(3)

        month = months[month_name]

        if year:
            year = int(year)
        else:
            year = today.year

        try:
            result = datetime(
                year,
                month,
                day
            ).date()

            return result.isoformat()

        except ValueError:
            pass

    return None


# ============================================================
# DESCRIPTION
# ============================================================

def extract_description(text):
    """
    Extract description if user explicitly provides one.
    """

    match = re.search(
        r"(?:description|about)\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return ""


# ============================================================
# ALL PARAMETERS
# ============================================================

def extract_parameters(text):

    return {
        "course": extract_course(text),
        "title": extract_title(text),
        "due_date": extract_due_date(text),
        "description": extract_description(text),
        "task_type": extract_task_type(text)
    }
# ============================================================
# AVAILABLE STUDY TIME
# ============================================================

def extract_available_minutes(text):
    """
    Extract available study time from natural language.

    Examples:

        "I have 3 hours"          -> 180
        "I have 2 hours today"    -> 120
        "I have 90 minutes"       -> 90
        "I can study for 45 mins" -> 45
        "I have 1.5 hours"        -> 90
        "I have 30m"              -> 30
    """

    import re

    text_lower = text.lower().strip()

    # --------------------------------------------------------
    # HOURS
    # --------------------------------------------------------

    hour_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|hr|h)\b",
        text_lower
    )

    if hour_match:

        hours = float(
            hour_match.group(1)
        )

        return int(
            hours * 60
        )

    # --------------------------------------------------------
    # MINUTES
    # --------------------------------------------------------

    minute_match = re.search(
        r"(\d+)\s*(?:minutes?|mins?|min|m)\b",
        text_lower
    )

    if minute_match:

        return int(
            minute_match.group(1)
        )

    return None