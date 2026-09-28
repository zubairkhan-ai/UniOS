import re


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    text = text.lower()

    text = (
        text
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(":", "")
        .replace(".", "")
        .replace("-", " ")
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# EXTRACT TERM
# =========================================================

def extract_term(question):

    question_clean = (
        question
        .lower()
        .strip()
        .replace("?", "")
    )

    patterns = [
        r"^what is (.+)$",
        r"^what are (.+)$",
        r"^define (.+)$",
        r"^definition of (.+)$",
        r"^meaning of (.+)$"
    ]

    for pattern in patterns:

        match = re.match(
            pattern,
            question_clean
        )

        if match:

            return match.group(1).strip()

    return None


# =========================================================
# REMOVE HEADING NUMBER
# =========================================================

def remove_heading_number(text):

    return re.sub(
        r"^\d+(\.\d+)*\s+",
        "",
        text
    ).strip()


# =========================================================
# EXACT HEADING
# =========================================================

def is_exact_heading(
    line,
    term
):

    cleaned_line = (
        remove_heading_number(line)
    )

    return (
        normalize_text(cleaned_line)
        ==
        normalize_text(term)
    )


# =========================================================
# DEFINITION SENTENCE
# =========================================================

def is_definition_sentence(
    line,
    term
):

    normalized_line = normalize_text(
        line
    )

    normalized_term = normalize_text(
        term
    )

    if not normalized_term:

        return False

    padded_line = (
        " "
        + normalized_line
        + " "
    )

    # -----------------------------------------
    # Term must actually appear
    # -----------------------------------------

    if normalized_term not in normalized_line:

        return False

    # -----------------------------------------
    # Definition indicators
    # -----------------------------------------

    indicators = [
        " is ",
        " are ",
        " means ",
        " refers to ",
        " called ",
        " defined as ",
        " stands for "
    ]

    for indicator in indicators:

        if indicator in padded_line:

            return True

    return False


# =========================================================
# VALIDATE POSSIBLE DEFINITION
# =========================================================

def is_valid_definition(line: str, term: str) -> bool:
    """
    Check whether a line is a real definition rather than
    a heading, question, or incomplete fragment.
    """

    if not line:
        return False

    text = line.strip()
    lower = text.lower()

    # Too short to be a useful definition
    if len(text.split()) < 5:
        return False

    # Reject questions
    if text.endswith("?"):
        return False

    question_starters = (
        "what ",
        "how ",
        "why ",
        "when ",
        "where ",
        "which ",
        "who ",
    )

    if lower.startswith(question_starters):
        return False

    # Reject common heading-style lines
    if is_exact_heading(text, term):
        return False

    # Definition indicators
    definition_indicators = (
        " is ",
        " are ",
        " means ",
        " refers to ",
        " defined as ",
        " stands for ",
        " called ",
    )

    # Normal definition sentence
    if any(indicator in lower for indicator in definition_indicators):
        return True

    return False

# =========================================================
# EXTRACT DEFINITION
# =========================================================
def extract_definition(question: str, documents) -> str | None:
    """
    Extract the most direct definition from the lecture material.

    Priority:
    1. A definition immediately following a matching question heading.
    2. A definition immediately following a definition heading.
    3. A normal definition sentence.
    """

    term = extract_term(question)

    if not term:
        return None

    normalized_term = normalize_text(term)

    # =========================================================
    # PASS 1 — Heading followed by direct definition
    # =========================================================

    for doc in documents:

        lines = [
            line.strip()
            for line in doc.page_content.splitlines()
            if line.strip()
        ]

        for i, line in enumerate(lines):

            normalized_line = normalize_text(line)

            # -------------------------------------------------
            # Normalize "an operating system" -> "operating system"
            # -------------------------------------------------

            heading_text = normalized_line

            if heading_text.startswith("what is "):
                heading_text = heading_text[len("what is "):]

            if heading_text.endswith("?"):
                heading_text = heading_text[:-1].strip()

            if heading_text.startswith("the "):
                heading_text = heading_text[4:].strip()

            if heading_text.startswith("an "):
                heading_text = heading_text[3:].strip()

            if heading_text.startswith("a "):
                heading_text = heading_text[2:].strip()

            # -------------------------------------------------
            # Check whether this is the requested topic heading
            # -------------------------------------------------

            is_matching_heading = (
                heading_text == normalized_term
                or heading_text == f"{normalized_term} definition"
                or heading_text == f"definition of {normalized_term}"
                or heading_text == f"{normalized_term} cont"
            )

            if not is_matching_heading:
                continue

            # -------------------------------------------------
            # Look at the next few lines
            # -------------------------------------------------

            for next_line in lines[i + 1:i + 4]:

                if next_line.endswith("?"):
                    continue

                next_lower = next_line.lower()

                if next_lower.startswith((
                    "what ",
                    "how ",
                    "why ",
                    "when ",
                    "where ",
                    "which ",
                    "who ",
                )):
                    continue

                if is_exact_heading(next_line, term):
                    continue

                # Direct definition phrase
                if len(next_line.split()) >= 7:
                    return next_line

    # =========================================================
    # PASS 2 — Normal definition sentence
    # =========================================================

    for doc in documents:

        lines = [
            line.strip()
            for line in doc.page_content.splitlines()
            if line.strip()
        ]

        for line in lines:

            if is_valid_definition(line, term):
                return line

    return None
# =========================================================
# EXTRACT EXPLICIT ADVANTAGES
# =========================================================

def extract_advantages(documents):

    answers = []

    for document in documents:

        lines = [
            line.strip()
            for line in document.page_content.splitlines()
            if line.strip()
        ]

        for line in lines:

            lower = line.lower()

            if (
                "advantage:" in lower
                or "advantage :" in lower
            ):

                cleaned = re.sub(
                    r"^.*?advantage\s*:\s*",
                    "",
                    line,
                    flags=re.IGNORECASE
                ).strip()

                if cleaned:

                    answers.append(
                        cleaned
                    )

    # -----------------------------------------
    # Remove duplicates
    # -----------------------------------------

    unique_answers = []

    for answer in answers:

        if answer not in unique_answers:

            unique_answers.append(
                answer
            )

    if not unique_answers:

        return None

    return "\n".join(
        f"- {answer}"
        for answer in unique_answers
    )


# =========================================================
# EXTRACT EXPLICIT DISADVANTAGES
# =========================================================

def extract_disadvantages(documents):

    answers = []

    for document in documents:

        lines = [
            line.strip()
            for line in document.page_content.splitlines()
            if line.strip()
        ]

        for line in lines:

            lower = line.lower()

            if (
                "disadvantage:" in lower
                or "disadvantage :" in lower
            ):

                cleaned = re.sub(
                    r"^.*?disadvantage\s*:\s*",
                    "",
                    line,
                    flags=re.IGNORECASE
                ).strip()

                if cleaned:

                    answers.append(
                        cleaned
                    )

    # -----------------------------------------
    # Remove duplicates
    # -----------------------------------------

    unique_answers = []

    for answer in answers:

        if answer not in unique_answers:

            unique_answers.append(
                answer
            )

    if not unique_answers:

        return None

    return "\n".join(
        f"- {answer}"
        for answer in unique_answers
    )