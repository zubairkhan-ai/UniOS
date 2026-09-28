from pathlib import Path
import json


# ============================================================
# SETTINGS
# ============================================================

MAX_HISTORY = 10

GRAPH_DIR = Path(__file__).resolve().parent

MEMORY_FILE = (
    GRAPH_DIR / "memory_store.json"
)


# ============================================================
# CREATE / LOAD MEMORY
# ============================================================

def create_memory():

    if not MEMORY_FILE.exists():

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4
            )

        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            memory = json.load(file)

        if isinstance(memory, list):
            return memory

        return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ============================================================
# SAVE
# ============================================================

def save_memory(history):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError as error:

        print(
            f"Warning: Could not save memory: {error}"
        )


# ============================================================
# ADD MEMORY
# ============================================================

def add_to_memory(
    history,
    user_message,
    ai_message,
    memory_type="conversation",
    intent=None
):

    entry = {
        "type": memory_type,
        "user": user_message,
        "ai": ai_message
    }

    if intent:
        entry["intent"] = intent

    history.append(entry)

    if len(history) > MAX_HISTORY:
        history = history[
            -MAX_HISTORY:
        ]

    save_memory(history)

    return history


# ============================================================
# RAG MEMORY
# ============================================================

def get_rag_memory(history):

    return [
        item
        for item in history
        if item.get("type") == "rag"
    ]


# ============================================================
# TOOL MEMORY
# ============================================================

def get_tool_memory(history):

    return [
        item
        for item in history
        if item.get("type") == "tool"
    ]


# ============================================================
# ALL MEMORY
# ============================================================

def get_memory(history):

    return history


# ============================================================
# CLEAR
# ============================================================

def clear_memory():

    history = []

    save_memory(history)

    return history