# main.py
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
import sys
import gi
import json
from pathlib import Path
import uuid
import shutil

gi.require_version('Gtk', '4.0')
gi.require_version("Adw", '1')
gi.require_version('Xdp', '1.0')

from gi.repository import Gtk, Gio, Adw, Xdp
from .window import WebAppsWindow
from .web_app_window import WebAppWindow
from .create_desktop_file import desktop_filer

class WebappsApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, args):
        if len(args) > 1 and args[1] + '.json' in os.listdir('.var/app/net.codelogistics.webapps/webapps/'):
            super().__init__(application_id='net.codelogistics.webapps.' + args[1],
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        else:
            super().__init__(application_id='net.codelogistics.webapps.Webapps',
                             flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('close', self.close_stuff_by_escape, ['Escape'])
        self.create_action('about', self.on_about_action)
        self.args = args

    def close_stuff_by_escape(self, action, data):
        if type(self.get_active_window()) == WebAppsWindow:
            window = self.get_active_window()
            if window.get_visible_dialog():
                window.get_visible_dialog().close()

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.update_desktop_files()

        if len(os.listdir('.var/app/net.codelogistics.webapps/webapps/')) and not os.path.exists('.var/app/net.codelogistics.webapps/webapps/' + 'uuid_verified'):
            self.update_old_webapps()

        with open('.var/app/net.codelogistics.webapps/webapps/' + 'uuid_verified', 'w') as f:
                f.write('')

        if len(self.args) > 1 and self.args[1] + '.json' in os.listdir('.var/app/net.codelogistics.webapps/webapps'):
            with open('.var/app/net.codelogistics.webapps/webapps/' + self.args[1] + '.json', 'r') as f:                
                state = json.load(f)
            win = WebAppWindow(application=self, state = state)
            win.present()

        else:
            win = WebAppsWindow(application=self)
            win.present()

    def update_old_webapps(self):
        # update files in old format (name.json) to new format (uuid.json)
        for i in os.listdir(os.path.expanduser('~/.var/app/net.codelogistics.webapps/webapps/')):
            if not i.endswith('json') or i.endswith('.permissions.json'):
                continue
            print('Updating {} to new format...', i)
            app_id = str(uuid.uuid4())
            i = i[:-5]
            pre = os.path.expanduser('~/.var/app/net.codelogistics.webapps/webapps/')
            shutil.move(pre + i + '.json', pre + app_id + '.json')
            with open(pre + app_id + '.json', 'r') as f:
                config = json.load(f)
            
            config['app_id']  = app_id

            with open(pre + app_id + '.json', 'w') as f:
                json.dump(config, f)

            try:
                shutil.move(pre + i + '.window', pre + app_id + '.window')
            except Exception as e:
                print(e)
            try:
                shutil.move(pre + i + '.cookies.txt', pre + app_id + '.cookies.txt')
            except Exception as e:
                print(e)
            try:
                shutil.move(pre + i + '.permissions.json', pre + app_id + '.permissions.json')
            except Exception as e:
                print(e)
            try:
                shutil.move(os.path.expanduser('~/.var/app/net.codelogistics.webapps/webapps/icons/192x192/net.codelogistics.webapps.') + i + '.png', os.path.expanduser('~/.var/app/net.codelogistics.webapps/webapps/icons/192x192/net.codelogistics.webapps.') + app_id + '.png')
            except Exception as e:
                print(e)

            portal = Xdp.Portal()
            try:
                portal.dynamic_launcher_uninstall("net.codelogistics.webapps." + i + ".desktop")
            except Exception as e:
                print(e)

            desktop_filer(self, app_id, i)

    def update_desktop_files(self):
        for i in os.listdir(os.path.expanduser("~/.local/share/applications")):
            if i.startswith("net.codelogistics.webapps."):
                if i[26:-8] + ".json" not in os.listdir(os.path.expanduser('~/.var/app/net.codelogistics.webapps/webapps/')):
                    try:
                        os.remove(os.path.expanduser("~/.local/share/applications/") + i)
                    except:
                        pass

                with open(os.path.expanduser("~/.local/share/applications/") + i, "r") as f:
                    file = f.read()

                if file.find("TryExec=") != -1:
                    lines = file.split("\n")

                    with open(os.path.expanduser("~/.local/share/applications/") + i, "w") as fo:
                        for i in range(0, len(lines)):
                            if lines[i].find("TryExec=") != -1:
                                pass
                            else:
                                fo.write(lines[i] + "\n")

    def on_about_action(self, widget, data):
        """Callback for the app.about action."""
        about = Adw.AboutDialog()
        about.set_application_name(_("Web Apps"))
        about.set_comments(_("Install websites as apps"))
        about.set_developer_name("Satvik Patwardhan")
        about.set_application_icon('net.codelogistics.webapps')
        about.set_version('0.5.3')
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_developers(['Satvik Patwardhan'])
        about.set_copyright('© 2024 Satvik Patwardhan')
        about.set_website("https://codelogistics.net/")
        about.set_issue_url("https://codeberg.org/eyekay/webapps/issues")
        # Translators: add your name here
        about.set_translator_credits(_("Satvik Patwardhan"))

        about.present(self.get_active_window())

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""

    Path(".var/app/net.codelogistics.webapps/webapps/").mkdir(parents=True, exist_ok=True)
    Path(".var/app/net.codelogistics.webapps/icons/192x192/").mkdir(parents=True, exist_ok=True)

    app = WebappsApplication(args = sys.argv)
    return app.run()


