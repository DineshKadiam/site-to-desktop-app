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

import threading
import time
import os
import shutil
import sys
import gi
import json
import stat

from gi.repository import Gtk, GLib, Gio, Xdp

def desktop_filer(parent, app_id, name):

    icon_path = os.path.expanduser('~/.var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps.' + app_id + '.png')
    write_desktop_file(parent, app_id, name, icon_path)

def write_desktop_file(parent, app_id, name, icon_path):
    def get_result(portal, result):
        try:
            variant = portal.dynamic_launcher_prepare_install_finish(result)
            token = variant['token']

            desktop_file = '[Desktop Entry]\nExec = webapps {}\nTerminal=false\nType=Application\nCategories=Network;'.format(app_id)

            portal.dynamic_launcher_install(token, "net.codelogistics.webapps." + app_id + ".desktop", desktop_file)
        except Exception as e:
            if os.path.exists('.var/app/net.codelogistics.webapps/webapps/' + app_id + '.window'):
                # Window has been opened atleast once
                pass
            else:
                if os.path.exists('.var/app/net.codelogistics.webapps/webapps/' + app_id + '.json'):
                    os.remove('.var/app/net.codelogistics.webapps/webapps/' + app_id + '.json')
                if os.path.exists('.var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps.' + app_id + '.png'):
                    os.remove('.var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps.' + app_id + '.png')
                parent.refresh_rows()

            # Translators: Do not translate portal
            print(_("Portal error:"), e)
            return

    portal = Xdp.Portal()

    with open(icon_path, 'rb') as f:
        bytes_data = f.read()
        icon = Gio.BytesIcon.new(GLib.Bytes.new(bytes_data)).serialize()

    portal.dynamic_launcher_prepare_install(None, name, icon, Xdp.LauncherType.APPLICATION, None, False, False, None, get_result)
