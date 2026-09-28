from pathlib import Path
import re

from langchain_chroma import Chroma
from .embeddings import get_embeddings


# =========================================================
# CONFIGURATION
# =========================================================

TOP_K = 3

# Maximum Chroma distance allowed
MAX_DISTANCE = 0.90

# Minimum number of meaningful query words that should
# overlap with retrieved document text.
MIN_KEYWORD_MATCHES = 1

# Minimum number of words required before a document
# can be considered meaningful explanatory content.
MIN_CONTENT_WORDS = 12


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
# TEXT HELPERS
# =========================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# QUERY KEYWORDS
# =========================================================

def get_query_keywords(question):

    stop_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "of",
        "to",
        "in",
        "on",
        "for",
        "and",
        "or",
        "how",
        "does",
        "do",
        "why",
        "when",
        "where",
        "which",
        "who",
        "can",
        "could",
        "would",
        "should",
        "it",
        "this",
        "that",
        "its",
        "their",
        "with",
        "from",
        "be",
        "used",
        "use",
        "work",
        "works"
    }

    words = normalize_text(
        question
    ).split()

    keywords = [

        word

        for word in words

        if (
            len(word) >= 3
            and word not in stop_words
        )

    ]

    return set(keywords)


# =========================================================
# KEYWORD MATCH COUNT
# =========================================================

def keyword_match_count(
    question,
    document
):

    query_keywords = get_query_keywords(
        question
    )

    if not query_keywords:

        return 0

    document_text = normalize_text(
        document.page_content
    )

    matches = 0

    for keyword in query_keywords:

        if keyword in document_text:

            matches += 1

    return matches


# =========================================================
# DOCUMENT WORD COUNT
# =========================================================

def get_word_count(document):

    text = normalize_text(
        document.page_content
    )

    if not text:

        return 0

    return len(
        text.split()
    )


# =========================================================
# OUTLINE / INDEX DETECTION
# =========================================================

def is_outline_document(document):

    text = normalize_text(
        document.page_content
    )

    word_count = len(
        text.split()
    )

    # -----------------------------------------
    # Very small chunks are often headings,
    # indexes, or course-outline material.
    # -----------------------------------------

    if word_count < MIN_CONTENT_WORDS:

        return True

    # -----------------------------------------
    # Common outline indicators
    # -----------------------------------------

    outline_indicators = [

        "course outline",

        "lecture outline",

        "topics covered",

        "table of contents",

        "contents"

    ]

    for indicator in outline_indicators:

        if indicator in text:

            return True

    return False


# =========================================================
# EXPLANATORY CONTENT CHECK
# =========================================================

def has_explanatory_content(
    question,
    document
):

    text = document.page_content.strip()

    if not text:

        return False

    # -----------------------------------------
    # Reject very short chunks
    # -----------------------------------------

    if get_word_count(document) < MIN_CONTENT_WORDS:

        return False

    # -----------------------------------------
    # Reject obvious outline/index content
    # -----------------------------------------

    if is_outline_document(document):

        return False

    normalized = normalize_text(
        text
    )

    query_keywords = get_query_keywords(
        question
    )

    if not query_keywords:

        return False

    # -----------------------------------------
    # Definition/explanation indicators
    # -----------------------------------------

    definition_patterns = [

        " is ",

        " are ",

        " means ",

        " refers to ",

        " defined as ",

        " consists of ",

        " responsible for ",

        " used to ",

        " allows ",

        " provides ",

        " enables "

    ]

    padded_text = (
        " "
        + normalized
        + " "
    )

    for pattern in definition_patterns:

        if pattern in padded_text:

            if any(
                keyword in normalized
                for keyword in query_keywords
            ):

                return True

    # -----------------------------------------
    # Multiple sentence evidence
    # -----------------------------------------

    sentence_count = len(
        re.findall(
            r"[.!?]",
            text
        )
    )

    if sentence_count >= 2:

        if any(
            keyword in normalized
            for keyword in query_keywords
        ):

            return True

    # -----------------------------------------
    # Longer paragraph evidence
    # -----------------------------------------

    if get_word_count(document) >= 30:

        if any(
            keyword in normalized
            for keyword in query_keywords
        ):

            return True

    return False


# =========================================================
# RETRIEVE DOCUMENTS
# =========================================================

def retrieve_documents(
    question,
    course=None,
    week=None,
    question_type=None
):

    search_kwargs = {
        "k": 5
    }

    # =====================================================
    # METADATA FILTER
    # =====================================================

    if (
        course is not None
        and week is not None
    ):

        search_kwargs["filter"] = {

            "$and": [

                {
                    "course": course
                },

                {
                    "week": week
                }

            ]

        }

    elif course is not None:

        search_kwargs["filter"] = {

            "course": course

        }

    elif week is not None:

        search_kwargs["filter"] = {

            "week": week

        }

    # =====================================================
    # SIMILARITY SEARCH
    # =====================================================

    results_with_scores = (

        vector_store
        .similarity_search_with_score(
            question,
            **search_kwargs
        )

    )

    # =====================================================
    # PRINT RETRIEVAL SCORES
    # =====================================================

    print(
        "\n-----------------------------------"
    )

    print(
        "RETRIEVAL SCORES"
    )

    print(
        "-----------------------------------"
    )

    for document, score in results_with_scores:

        course_name = document.metadata.get(
            "course",
            "Unknown"
        )

        week_name = document.metadata.get(
            "week",
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

        keyword_matches = (
            keyword_match_count(
                question,
                document
            )
        )

        word_count = get_word_count(
            document
        )

        explanatory = (
            has_explanatory_content(
                question,
                document
            )
        )

        print(
            f"Course: {course_name} | "
            f"Week: {week_name} | "
            f"{location} | "
            f"Distance: {score:.4f} | "
            f"Keyword Matches: {keyword_matches} | "
            f"Words: {word_count} | "
            f"Explanatory: {explanatory}"
        )

    # =====================================================
    # FILTER + DEDUPLICATE
    # =====================================================

    documents = []

    seen = set()

    for document, score in results_with_scores:

        # -------------------------------------
        # DISTANCE CHECK
        # -------------------------------------

        if score > MAX_DISTANCE:

            continue

        # -------------------------------------
        # KEYWORD EVIDENCE CHECK
        # -------------------------------------

        keyword_matches = (
            keyword_match_count(
                question,
                document
            )
        )

        if keyword_matches < MIN_KEYWORD_MATCHES:

            continue

        # -------------------------------------
        # DEFINITION EVIDENCE CHECK
        #
        # Only apply this stricter rule to
        # definition questions.
        # -------------------------------------

        if question_type == "definition":

            if not has_explanatory_content(
                question,
                document
            ):

                continue

        # -------------------------------------
        # SOURCE INFORMATION
        # -------------------------------------

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

        unique_id = (
            source,
            slide,
            page
        )

        # -------------------------------------
        # DEDUPLICATION
        # -------------------------------------

        if unique_id in seen:

            continue

        seen.add(
            unique_id
        )

        # -------------------------------------
        # ADD DOCUMENT
        # -------------------------------------

        documents.append(
            document
        )

        # -------------------------------------
        # TOP K
        # -------------------------------------

        if len(documents) >= TOP_K:

            break

    # =====================================================
    # FINAL STATUS
    # =====================================================

    print(
        f"\n[RETRIEVER] Accepted documents: "
        f"{len(documents)}"
    )

    return documents