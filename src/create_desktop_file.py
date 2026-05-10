# create_desktop_file.py
#
# Copyright 2023 Satvik Patwardhan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, GLib, Xdp

from . import web_app_paths as paths
from .web_app_paths import APP_ID


def name_desktop_file(app_id):
    return f"{APP_ID}.{app_id}.desktop"


def desktop_filer(parent, app_id, name):
    write_desktop_file(parent, app_id, name, paths.app_icon_file(app_id))


def write_desktop_file(parent, app_id, name, icon_path):
    def get_result(portal, result):
        try:
            variant = portal.dynamic_launcher_prepare_install_finish(result)
            token = variant["token"]
            desktop_file_content = f"[Desktop Entry]\nExec =webapps {app_id}\nTerminal=false\nType=Application\nCategories=Network;"
            portal.dynamic_launcher_install(token, name_desktop_file(app_id), desktop_file_content)

        except Exception as e:
            if paths.app_window_state(app_id).exists():
                # Window has been opened at least once
                pass
            else:
                paths.app_state(app_id).unlink(missing_ok=True)
                paths.app_icon_file(app_id).unlink(missing_ok=True)
                parent.refresh_rows()

            # Translators: Do not translate portal
            print(_("Portal error:"), e)
            return

    with open(icon_path, "rb") as f:
        icon = Gio.BytesIcon.new(GLib.Bytes.new(f.read())).serialize()

        Xdp.Portal.new().dynamic_launcher_prepare_install(
            None,
            name,
            icon,
            Xdp.LauncherType.APPLICATION,
            None,
            False,
            False,
            None,
            get_result,
        )


def uninstall_desktop_file(name):
    try:
        Xdp.Portal.new().dynamic_launcher_uninstall(name)
    except Exception as e:
        # Translators: Do not translate portal
        print(_("Portal error:"), e)
        return
