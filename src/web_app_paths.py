from pathlib import Path

from gi.repository import GLib

APP_ID = "net.codelogistics.webapps"

XDG_DATA_DIR = Path(GLib.get_user_data_dir())
XDG_CACHE_DIR = Path(GLib.get_user_cache_dir())

WEBAPPS_DATA_DIR = XDG_DATA_DIR / "webapps"
WEBAPPS_CACHE_DIR = XDG_CACHE_DIR / "webapps"
ICONS_DIR = XDG_DATA_DIR / "icons" / "192x192"


def app_data_dir(app_id):
    return WEBAPPS_DATA_DIR / app_id


def app_cache_dir(app_id):
    return WEBAPPS_CACHE_DIR / app_id


def app_icon_file(app_id):
    return ICONS_DIR / f"{APP_ID}.{app_id}.png"


def app_webkitgtk_data(app_id):
    return app_data_dir(app_id) / "webkitgtk"


def app_webkitgtk_cache(app_id):
    return app_cache_dir(app_id) / "webkitgtk"


def app_webkitgtk_cookies(app_id):
    return app_data_dir(app_id) / "cookies.txt"


def app_state(app_id):
    return app_data_dir(app_id) / "state.json"


def app_window_state(app_id):
    return app_data_dir(app_id) / "window.state"


def app_permissions_state(app_id):
    return app_data_dir(app_id) / "permissions.json"
