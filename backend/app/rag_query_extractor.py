import re


def extract_rag_query(user_input: str) -> str:
    """
    Extract the knowledge/lecture part from a hybrid query.
    """

    text = user_input.strip()

    # ---------------------------------------------------------
    # Tool requests that begin with "and"
    # ---------------------------------------------------------

    patterns = [
        r"\s+and\s+make\s+me\s+(?:a\s+)?\d+(?:\.\d+)?\s*"
        r"(?:hour|hours|hr|hrs|minute|minutes)\s+"
        r"(?:study\s+)?plan\b",

        r"\s+and\s+(?:make|create)\s+(?:a\s+)?"
        r"(?:study\s+)?plan\b",

        r"\s+and\s+(?:show|list|tell me|give me)\s+my\b",

        r",\s*(?:show|list|tell me|give me)\s+my\b",

        r",\s*(?:make|create|give me)\s+"
        r"(?:a\s+)?(?:study\s+)?plan\b",

        r"\s+and\s+i\s+have\s+\d+",
    ]

    # Find the earliest tool-request position.
    positions = []

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            positions.append(match.start())

    if positions:
        text = text[:min(positions)]

    return text.strip()