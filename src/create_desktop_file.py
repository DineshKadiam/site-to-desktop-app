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

import os

from gi.repository import Gio, GLib, Xdp


def desktop_filer(parent, app_id, name):
    icon_path = os.path.expanduser(
        "~/.var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps."
        + app_id
        + ".png"
    )
    write_desktop_file(parent, app_id, name, icon_path)


def get_result(portal, result):
    try:
        variant = portal.dynamic_launcher_prepare_install_finish(result)
        token = variant["token"]
        # we will replace true with webapps later : https://github.com/flatpak/xdg-desktop-portal/issues/1674
        desktop_file = "[Desktop Entry]\nExec = true {}\nTerminal=false\nType=Application\nCategories=Network;".format(
            app_id
        )

        portal.dynamic_launcher_install(
            token, "net.codelogistics.webapps." + app_id + ".desktop", desktop_file
        )
        with open(
            os.path.expanduser(
                "~/.local/share/applications/net.codelogistics.webapps.{}.desktop".format(
                    app_id
                )
            ),
            "r",
        ) as f:
            desktop_file = f.read().replace("--command=true", "")
        with open(
            os.path.expanduser(
                "~/.local/share/applications/net.codelogistics.webapps.{}.desktop".format(
                    app_id
                )
            ),
            "w",
        ) as f:
            f.write(desktop_file)

    except Exception as e:
        if os.path.exists(
            ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".window"
        ):
            # Window has been opened atleast once
            pass
        else:
            if os.path.exists(
                ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".json"
            ):
                os.remove(
                    ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".json"
                )
            if os.path.exists(
                ".var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps."
                + app_id
                + ".png"
            ):
                os.remove(
                    ".var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps."
                    + app_id
                    + ".png"
                )
            parent.refresh_rows()

        # Translators: Do not translate portal
        print(_("Portal error:"), e)
        return


def write_desktop_file(parent, app_id, name, icon_path):
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
