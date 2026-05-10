import json
from pathlib import Path

from . import web_app_paths as paths


def save_state(state):
    # convert Path to str
    state["icon"] = str(state["icon"])

    path = paths.app_state(state["app_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(state, f)


def load_state(app_id):
    path = paths.app_state(app_id)
    if not path.exists():
        return None

    with path.open("r") as f:
        try:
            state = json.load(f)
        except json.JSONDecodeError | UnicodeDecodeError:
            # Translators: Keep the {} as it is
            print(_("File {} broken! Maybe it was modified locally?").format(path))
            return None

    assert state["app_id"] == app_id
    state["icon"] = Path(state["icon"])
    return state


def states():
    for app_id in paths.app_ids():
        state = load_state(app_id)
        if state is not None:
            yield state


def save_window_state(app_id, maximized, width, height, k=1.0):
    path = paths.app_window_state(app_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as restore_file:
        restore_file.write(str(maximized))
        restore_file.write("\n")
        restore_file.write(f"{width}x{height}")
        restore_file.write("\n")
        restore_file.write(str(k))


def load_window_state(app_id):
    path = paths.app_window_state(app_id)
    if not path.exists():
        return None

    return path.read_text().splitlines()


def save_permissions(app_id, permissions):
    path = paths.app_permissions_state(app_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(permissions, f)


def load_permissions(app_id):
    path = paths.app_permissions_state(app_id)
    if not path.exists():
        return None

    with path.open("r") as f:
        state = json.load(f)
    return state
