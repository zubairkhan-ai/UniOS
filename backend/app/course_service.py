from pathlib import Path


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LECTURES_DIR = PROJECT_ROOT / "data" / "lectures"


# =========================================================
# COURSE NAMES
# =========================================================

COURSE_NAMES = {
    "DAA": "Design & Analysis of Algorithms",
    "OOP": "Object Oriented Programming",
    "OS": "Operating Systems",
    "web and ai": "Web & AI",
}


# =========================================================
# SUPPORTED LECTURE FILES
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".ppt",
    ".pptx",
    ".doc",
    ".docx",
}


# =========================================================
# GET COURSES
# =========================================================

def get_courses():

    courses = []

    if not LECTURES_DIR.exists():

        print(
            f"[Courses] Lecture directory not found: {LECTURES_DIR}"
        )

        return courses


    # =====================================================
    # SCAN COURSE FOLDERS
    # =====================================================

    for course_dir in sorted(
        LECTURES_DIR.iterdir()
    ):

        if not course_dir.is_dir():
            continue


        course_code = course_dir.name


        # =================================================
        # FIND WEEK FOLDERS
        # =================================================

        week_folders = [
            folder
            for folder in course_dir.iterdir()
            if folder.is_dir()
        ]


        # =================================================
        # FIND LECTURE FILES
        # =================================================

        lecture_files = []

        for week_folder in week_folders:

            for file in week_folder.rglob("*"):

                if (
                    file.is_file()
                    and file.suffix.lower()
                    in SUPPORTED_EXTENSIONS
                ):

                    lecture_files.append(file)


        # =================================================
        # COURSE DATA
        # =================================================

        course = {

            "code": course_code,

            "name": COURSE_NAMES.get(
                course_code,
                course_code
            ),

            "instructor": "Course Instructor",

            "credits": 3,

            "weeks": len(week_folders),

            "lectures": len(lecture_files),

        }


        courses.append(course)


    print(
        f"[Courses] Found {len(courses)} courses"
    )


    return courses
# =========================================================
# GET COURSE DETAILS
# =========================================================

def get_course_details(course_code):

    course_dir = LECTURES_DIR / course_code

    if not course_dir.exists() or not course_dir.is_dir():
        return None


    weeks = []


    # =====================================================
    # SCAN WEEK FOLDERS
    # =====================================================

    for week_dir in sorted(course_dir.iterdir()):

        if not week_dir.is_dir():
            continue


        lectures = []


        # =================================================
        # SCAN LECTURE FILES
        # =================================================

        for file in sorted(week_dir.rglob("*")):

            if not file.is_file():
                continue


            if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue


            lectures.append({
                "name": file.name,
                "type": file.suffix.lower().replace(".", ""),
                "path": str(file.relative_to(PROJECT_ROOT)),
            })


        weeks.append({
            "name": week_dir.name,
            "lectures": lectures,
        })


    return {
        "code": course_code,
        "name": COURSE_NAMES.get(
            course_code,
            course_code
        ),
        "weeks": weeks,
    }