from pathlib import Path
import json


# ============================================================
# SETTINGS
# ============================================================

GRAPH_DIR = Path(__file__).resolve().parent

STATE_FILE = GRAPH_DIR / "state_store.json"


# ============================================================
# DEFAULT STATE
# ============================================================

DEFAULT_STATE = {
    "current_study_task": None,
    "pending_request": None
}


# ============================================================
# LOAD STATE
# ============================================================

def load_state():

    if not STATE_FILE.exists():

        save_state(DEFAULT_STATE)

        return DEFAULT_STATE.copy()

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            state = json.load(file)

        if not isinstance(state, dict):

            return DEFAULT_STATE.copy()

        return {
            "current_study_task": state.get(
                "current_study_task"
            ),
            "pending_request": state.get(
                "pending_request"
            )
        }

    except (
        json.JSONDecodeError,
        OSError
    ):

        return DEFAULT_STATE.copy()


# ============================================================
# SAVE STATE
# ============================================================

def save_state(
    current_study_task=None,
    pending_request=None
):

    state = {
        "current_study_task": current_study_task,
        "pending_request": pending_request
    }

    try:

        with open(
            STATE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                state,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError as error:

        print(
            f"Warning: Could not save state: {error}"
        )


# ============================================================
# CLEAR STATE
# ============================================================

def clear_state():

    save_state(
        current_study_task=None,
        pending_request=None
    )