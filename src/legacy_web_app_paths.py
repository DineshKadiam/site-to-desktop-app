from collections.abc import Callable
from functools import wraps
from pathlib import Path
import shutil

APP_ID = "net.codelogistics.webapps"

XDG_DATA_DIR = Path.home() / ".var" / "app" / APP_ID

WEBAPPS_DATA_DIR = XDG_DATA_DIR / "webapps"
WEBAPPS_CACHE_DIR = XDG_DATA_DIR / "webapps"
ICONS_DIR = XDG_DATA_DIR / "icons" / "192x192"


def app_ids():
    for app_state_file in WEBAPPS_DATA_DIR.glob("*.json"):
        yield app_state_file.stem


def app_data_dir(app_id):
    return WEBAPPS_DATA_DIR


def app_cache_dir(app_id):
    return WEBAPPS_CACHE_DIR


def app_icon_file(app_id):
    return ICONS_DIR / f"{APP_ID}.{app_id}.png"


def app_webkitgtk_data(app_id):
    return app_data_dir(app_id) / f"{app_id}_data"


def app_webkitgtk_cache(app_id):
    return app_cache_dir(app_id) / f"{app_id}_cache"


def app_webkitgtk_cookies(app_id):
    return app_data_dir(app_id) / f"{app_id}.cookies.txt"


def app_state(app_id):
    return app_data_dir(app_id) / f"{app_id}.json"


def app_window_state(app_id):
    return app_data_dir(app_id) / f"{app_id}.window"


def app_permissions_state(app_id):
    return app_data_dir(app_id) / f"{app_id}.permissions.json"


def migrate_legacy_path(legacy_path_func: Callable[[str], Path]):
    def decorator(current_path_func: Callable[[str], Path]):
        @wraps(current_path_func)
        def wrapper(app_id: str) -> Path:
            current_path = current_path_func(app_id)
            legacy_path = legacy_path_func(app_id)
            if not current_path.exists() and legacy_path.exists():
                # Translators: first {} is the legacy path, second is the current path; both are necessary!
                print(_("Migrating: {} -> {}").format(legacy_path, current_path))
                current_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(legacy_path, current_path)

            return current_path

        return wrapper

    return decorator
