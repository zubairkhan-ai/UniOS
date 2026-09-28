from pathlib import Path

from langchain_chroma import Chroma

from .embeddings import get_embeddings


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# =========================================================
# CHROMA DATABASE
# =========================================================

CHROMA_DIR = (
    PROJECT_ROOT
    / "data"
    / "chroma_db"
)


# =========================================================
# LOAD EMBEDDINGS
# =========================================================

print("Loading embedding model...")

embeddings = get_embeddings()


# =========================================================
# CONNECT TO CHROMA
# =========================================================

print("Connecting to Chroma...")

vector_store = Chroma(
    persist_directory=str(CHROMA_DIR),
    collection_name="university_material",
    embedding_function=embeddings
)


# =========================================================
# GET ALL METADATA
# =========================================================

def get_available_metadata():

    # -----------------------------------------------------
    # ACCESS CHROMA COLLECTION
    # -----------------------------------------------------

    collection = vector_store._collection


    # -----------------------------------------------------
    # GET STORED DOCUMENTS
    # -----------------------------------------------------

    data = collection.get(
        include=["metadatas"]
    )


    metadatas = data.get(
        "metadatas",
        []
    )


    # -----------------------------------------------------
    # CREATE SETS
    # -----------------------------------------------------

    courses = set()

    weeks = set()


    # -----------------------------------------------------
    # EXTRACT COURSE AND WEEK
    # -----------------------------------------------------

    for metadata in metadatas:

        if not metadata:
            continue


        course = metadata.get(
            "course"
        )

        week = metadata.get(
            "week"
        )


        if course:
            courses.add(course)


        if week:
            weeks.add(week)


    # -----------------------------------------------------
    # SORT RESULTS
    # -----------------------------------------------------

    courses = sorted(courses)

    weeks = sorted(weeks)


    return courses, weeks


# =========================================================
# TEST
# =========================================================
# =========================================================
# GET WEEKS FOR A COURSE
# =========================================================

def get_weeks_for_course(course):

    collection = vector_store._collection

    data = collection.get(
        where={
            "course": course
        },
        include=["metadatas"]
    )

    metadatas = data.get(
        "metadatas",
        []
    )

    weeks = set()

    for metadata in metadatas:

        if not metadata:
            continue

        week = metadata.get(
            "week"
        )

        if week:
            weeks.add(week)

    return sorted(weeks)
# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("      AVAILABLE METADATA")
    print("===================================")

    courses, weeks = get_available_metadata()

    print("\nCourses:")

    for course in courses:
        print(
            f"- {course}"
        )

    print("\nAll Weeks:")

    for week in weeks:
        print(
            f"- {week}"
        )

    print("\nWeeks for DAA:")

    daa_weeks = get_weeks_for_course("DAA")

    for week in daa_weeks:
        print(
            f"- {week}"
        )