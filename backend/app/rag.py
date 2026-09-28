from .retriever import retrieve_documents

from .question_router import (
    classify_question
)

from .answer_extractor import (
    extract_definition,
    extract_advantages,
    extract_disadvantages
)

from .llm import generate_answer

from .question_rewriter import (
    rewrite_question
)

from .metadata_manager import (
    get_available_metadata,
    get_weeks_for_course
)


# =========================================================
# CHAT HISTORY
# =========================================================

chat_history = []


# =========================================================
# BUILD CONTEXT
# =========================================================

def build_context(documents):

    context_parts = []

    seen_sources = set()

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        course = document.metadata.get(
            "course",
            "Unknown"
        )

        week = document.metadata.get(
            "week",
            "Unknown"
        )

        slide = document.metadata.get(
            "slide"
        )

        page = document.metadata.get(
            "page"
        )

        document_type = document.metadata.get(
            "document_type",
            "unknown"
        )

        # -----------------------------------------
        # LOCATION
        # -----------------------------------------

        if slide is not None:

            location = (
                f"Slide {slide}"
            )

        elif page is not None:

            location = (
                f"Page {page}"
            )

        else:

            location = "Document"

        # -----------------------------------------
        # UNIQUE SOURCE
        # -----------------------------------------

        source_id = (
            source,
            slide,
            page
        )

        if source_id in seen_sources:

            continue

        seen_sources.add(
            source_id
        )

        text = (
            document
            .page_content
            .strip()
        )

        context_parts.append(

            f"[Course: {course} | "
            f"Week: {week} | "
            f"Source: {source} | "
            f"Type: {document_type} | "
            f"{location}]\n"
            f"{text}"

        )

    return "\n\n".join(
        context_parts
    )


# =========================================================
# UNIQUE SOURCES
# =========================================================

def get_unique_sources(documents):

    sources = []

    seen = set()

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        slide = document.metadata.get(
            "slide"
        )

        page = document.metadata.get(
            "page"
        )

        source_id = (
            source,
            slide,
            page
        )

        if source_id in seen:

            continue

        seen.add(
            source_id
        )

        sources.append(
            document
        )

    return sources


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(
    question,
    course=None,
    week=None,
    chat_history=None
):

    # -----------------------------------------------------
    # Make sure history is always a list
    # -----------------------------------------------------

    if chat_history is None:

        chat_history = []

    # =====================================================
    # REWRITE QUESTION
    # =====================================================

    retrieval_question = (
        rewrite_question(
            question,
            chat_history
        )
    )

    print(
        "\nRetrieval question:"
    )

    print(
        retrieval_question
    )

    # =====================================================
    # CLASSIFY QUESTION
    # =====================================================

    question_type = (
        classify_question(
            question
        )
    )

    print(
        "\nQuestion type:",
        question_type
    )

    # =====================================================
    # RETRIEVE
    # =====================================================

    documents = retrieve_documents(

        retrieval_question,

        course=course,

        week=week,

        question_type=question_type

    )

    # =====================================================
    # NO RESULTS
    # =====================================================

    if not documents:

        return (

            "The answer is not available in the "
            "provided lecture material.",

            []

        )

    # =====================================================
    # DEFINITION
    # =====================================================

    if question_type == "definition":

        # -------------------------------------------------
        # First try to find an explicit definition.
        # -------------------------------------------------

        answer = (
            extract_definition(
                retrieval_question,
                documents
            )
        )

        if answer:

            return (
                answer,
                documents
            )

        # -------------------------------------------------
        # Relevant explanatory evidence exists, but
        # there is no explicit definition sentence.
        #
        # Now let the LLM summarize ONLY the retrieved
        # lecture context.
        # -------------------------------------------------

        context = build_context(
            documents
        )

        print(
            "\n==================================="
        )

        print(
            "     LLM CONTEXT FOR DEFINITION"
        )

        print(
            "==================================="
        )

        print(
            context
        )

        print(
            "\n==================================="
        )

        print(
            "   END LLM DEFINITION CONTEXT"
        )

        print(
            "==================================="
        )

        answer = generate_answer(

            retrieval_question,

            context

        )

        return (
            answer,
            documents
        )

    # =====================================================
    # ADVANTAGE
    # =====================================================

    if question_type == "advantage":

        answer = (
            extract_advantages(
                documents
            )
        )

        if answer:

            return (
                answer,
                documents
            )

        # -------------------------------------------------
        # Fallback to grounded LLM
        # -------------------------------------------------

        context = build_context(
            documents
        )

        print(
            "\n==================================="
        )

        print(
            "      LLM CONTEXT FOR ADVANTAGE"
        )

        print(
            "==================================="
        )

        print(
            context
        )

        print(
            "\n==================================="
        )

        print(
            "   END LLM ADVANTAGE CONTEXT"
        )

        print(
            "==================================="
        )

        answer = generate_answer(

            retrieval_question,

            context

        )

        return (
            answer,
            documents
        )

    # =====================================================
    # DISADVANTAGE
    # =====================================================

    if question_type == "disadvantage":

        answer = (
            extract_disadvantages(
                documents
            )
        )

        if answer:

            return (
                answer,
                documents
            )

        # -------------------------------------------------
        # Fallback to grounded LLM
        # -------------------------------------------------

        context = build_context(
            documents
        )

        print(
            "\n==================================="
        )

        print(
            "    LLM CONTEXT FOR DISADVANTAGE"
        )

        print(
            "==================================="
        )

        print(
            context
        )

        print(
            "\n==================================="
        )

        print(
            "  END LLM DISADVANTAGE CONTEXT"
        )

        print(
            "==================================="
        )

        answer = generate_answer(

            retrieval_question,

            context

        )

        return (
            answer,
            documents
        )

    # =====================================================
    # GENERAL LLM CONTEXT
    # =====================================================

    context = build_context(
        documents
    )

    print(
        "\n==================================="
    )

    print(
        "         LLM CONTEXT"
    )

    print(
        "==================================="
    )

    print(
        context
    )

    print(
        "\n==================================="
    )

    print(
        "       END LLM CONTEXT"
    )

    print(
        "==================================="
    )

    # =====================================================
    # LLM
    # =====================================================

    answer = generate_answer(

        retrieval_question,

        context

    )

    return (
        answer,
        documents
    )


# =========================================================
# SELECT COURSE
# =========================================================

def select_course():

    courses, _ = (
        get_available_metadata()
    )

    if not courses:

        print(
            "No courses found in the database."
        )

        return None

    print(
        "\n==================================="
    )

    print(
        "        SELECT YOUR COURSE"
    )

    print(
        "==================================="
    )

    for index, course in enumerate(
        courses,
        start=1
    ):

        print(
            f"{index}. {course}"
        )

    while True:

        choice = input(
            "\nSelect course: "
        ).strip()

        if not choice.isdigit():

            print(
                "Please enter a number."
            )

            continue

        choice = int(
            choice
        )

        if (
            1
            <= choice
            <= len(courses)
        ):

            return courses[
                choice - 1
            ]

        print(
            "Invalid choice. Try again."
        )


# =========================================================
# SELECT WEEK
# =========================================================

def select_week(course):

    weeks = (
        get_weeks_for_course(
            course
        )
    )

    if not weeks:

        print(
            "No weeks found for this course."
        )

        return None

    print(
        "\n==================================="
    )

    print(
        f"        SELECT WEEK — {course}"
    )

    print(
        "==================================="
    )

    for index, week in enumerate(
        weeks,
        start=1
    ):

        print(
            f"{index}. {week}"
        )

    while True:

        choice = input(
            "\nSelect week: "
        ).strip()

        if not choice.isdigit():

            print(
                "Please enter a number."
            )

            continue

        choice = int(
            choice
        )

        if (
            1
            <= choice
            <= len(weeks)
        ):

            return weeks[
                choice - 1
            ]

        print(
            "Invalid choice. Try again."
        )


# =========================================================
# STANDALONE APPLICATION
# =========================================================

if __name__ == "__main__":

    print(
        "\n==================================="
    )

    print(
        "      AI UNIVERSITY RAG ASSISTANT"
    )

    print(
        "==================================="
    )

    CURRENT_COURSE = select_course()

    if CURRENT_COURSE is None:

        print(
            "Cannot start assistant."
        )

        exit()

    CURRENT_WEEK = select_week(
        CURRENT_COURSE
    )

    if CURRENT_WEEK is None:

        print(
            "Cannot start assistant."
        )

        exit()

    print(
        "\n==================================="
    )

    print(
        "       STUDY CONTEXT"
    )

    print(
        "==================================="
    )

    print(
        "Course:",
        CURRENT_COURSE
    )

    print(
        "Week:",
        CURRENT_WEEK
    )

    print(
        "\nType 'exit' to stop.\n"
    )

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    chat_history = []

    # -----------------------------------------------------
    # CHAT LOOP
    # -----------------------------------------------------

    while True:

        question = input(
            "You: "
        ).strip()

        if question.lower() == "exit":

            print(
                "Goodbye!"
            )

            break

        if not question:

            print(
                "Please enter a question.\n"
            )

            continue

        answer, sources = (
            ask_question(

                question,

                course=CURRENT_COURSE,

                week=CURRENT_WEEK,

                chat_history=chat_history

            )
        )

        # -------------------------------------------------
        # SAVE HISTORY
        # -------------------------------------------------

        chat_history.append({

            "user": question,

            "ai": answer

        })

        # -------------------------------------------------
        # PRINT ANSWER
        # -------------------------------------------------

        print(
            "\nAI:"
        )

        print(
            answer
        )

        # -------------------------------------------------
        # SOURCES
        # -------------------------------------------------

        print(
            "\nSources:"
        )

        unique_sources = (
            get_unique_sources(
                sources
            )
        )

        if unique_sources:

            for document in unique_sources:

                source = document.metadata.get(
                    "source",
                    "Unknown"
                )

                slide = document.metadata.get(
                    "slide"
                )

                page = document.metadata.get(
                    "page"
                )

                if slide is not None:

                    location = (
                        f"Slide {slide}"
                    )

                elif page is not None:

                    location = (
                        f"Page {page}"
                    )

                else:

                    location = "Document"

                print(
                    f"- {source} ({location})"
                )

        else:

            print(
                "- No relevant lecture material found."
            )

        print()