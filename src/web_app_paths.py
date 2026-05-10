from pathlib import Path

from gi.repository import GLib

from . import legacy_web_app_paths as legacy
from .legacy_web_app_paths import migrate_legacy_path

APP_ID = "net.codelogistics.webapps"

XDG_DATA_DIR = Path(GLib.get_user_data_dir())
XDG_CACHE_DIR = Path(GLib.get_user_cache_dir())

WEBAPPS_DATA_DIR = XDG_DATA_DIR / "webapps"
WEBAPPS_CACHE_DIR = XDG_CACHE_DIR / "webapps"
ICONS_DIR = XDG_DATA_DIR / "icons" / "192x192"

WEBAPPS_DATA_DIR.mkdir(parents=True, exist_ok=True)
WEBAPPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.mkdir(parents=True, exist_ok=True)


def app_ids():
    for app_folder in WEBAPPS_DATA_DIR.iterdir():
        if not app_folder.is_dir():
            continue
        yield app_folder.name

    yield from legacy.app_ids()


# Don't migrate: Migrate individual files/folders
def app_data_dir(app_id):
    return WEBAPPS_DATA_DIR / app_id


# Don't migrate: Migrate individual files/folders
def app_cache_dir(app_id):
    return WEBAPPS_CACHE_DIR / app_id


# Don't migrate icon files!
# The path to the icon file is stored in the state of the webapp.
# Icons are only moved when they are updated.
def app_icon_file(app_id):
    return ICONS_DIR / f"{APP_ID}.{app_id}.png"


@migrate_legacy_path(legacy.app_webkitgtk_data)
def app_webkitgtk_data(app_id):
    return app_data_dir(app_id) / "webkitgtk"


@migrate_legacy_path(legacy.app_webkitgtk_cache)
def app_webkitgtk_cache(app_id):
    return app_cache_dir(app_id) / "webkitgtk"


@migrate_legacy_path(legacy.app_webkitgtk_cookies)
def app_webkitgtk_cookies(app_id):
    return app_data_dir(app_id) / "cookies.txt"


@migrate_legacy_path(legacy.app_state)
def app_state(app_id):
    return app_data_dir(app_id) / "state.json"


@migrate_legacy_path(legacy.app_window_state)
def app_window_state(app_id):
    return app_data_dir(app_id) / "window.state"


@migrate_legacy_path(legacy.app_permissions_state)
def app_permissions_state(app_id):
    return app_data_dir(app_id) / "permissions.json"
