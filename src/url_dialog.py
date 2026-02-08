# url_dialog.py
#
# Copyright 2024 Satvik Patwardhan
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

import gi

gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk

from .create_web_app_dialog import CreateWebAppDialog
from .parse_manifest import get_website_data_from_manifest
from .parse_webpage import get_website_data_from_webpage


@Gtk.Template(resource_path="/net/codelogistics/webapps/url_dialog.ui")
class URLDialog(Adw.Dialog):
    __gtype_name__ = "URLDialog"

    url_entry = Gtk.Template.Child()
    add_button = Gtk.Template.Child()
    stack = Gtk.Template.Child()

    def __init__(self, parent_window, app):
        super().__init__()

        self.app = app
        self.parent_window = parent_window

        self.url_entry.connect("changed", self.enable_add_button)
        self.add_button.connect("clicked", self.add_webapp)
        self.set_default_widget(self.add_button)

        self.cancellable = None
        self.too_late_to_cancel = False

        self.connect("closed", self.cancelled)

    def enable_add_button(self, entry):
        test_url = entry.get_text()
        if test_url.strip() != "" and test_url.find(" ") == -1:
            if (
                test_url.find(".") != -1 and len(test_url.rpartition(".")[-1]) >= 2
            ) or (
                (test_url.startswith("http://") or test_url.startswith("https://"))
                and len(test_url[test_url.find("://") + 3 :]) >= 1
            ):
                self.add_button.set_sensitive(True)
                return

        self.add_button.set_sensitive(False)

    def add_webapp(self, button, data=None):
        active_dialog = self.app.get_active_window().get_visible_dialog()
        if type(active_dialog) == CreateWebAppDialog:
            if active_dialog.add_button.get_sensitive():
                active_dialog.add_button.activate()

        if not self.add_button.get_sensitive():  # for the shortcut
            return

        self.stack.set_visible_child_name("loading")

        GLib.idle_add(self.get_data)

    def get_data(self):
        url = self.url_entry.get_text()
        self.cancellable = Gio.Cancellable()
        manifest_data = get_website_data_from_manifest(self, url, self.cancellable)
        # this is an async function, it will call gotten_manifest_data()
        self.add_button.set_sensitive(False)

    def gotten_manifest_data(self, name, url, favicon, cancellable):
        if not cancellable.is_cancelled():
            if name == None or favicon == None:
                # manifest not found
                website_data = get_website_data_from_webpage(self, url, cancellable)
                # this is an async function, it will call gotten_website_data()
            else:
                state = {"name": name, "url": url, "icon": favicon}
                self.parent_window.show_create_window(self, state, False)

    def gotten_website_data(self, name, url, giveup, favicon, cancellable):
        if not cancellable.is_cancelled():
            if name == None:
                # title not found by html parser
                name = _("New Web App")
            if favicon == None:
                favicon = "/tmp/tmp_webapps_icon.png"

            state = {"name": name, "url": url, "icon": favicon}
            self.parent_window.show_create_window(self, state, giveup)

    def cancelled(self, dialog):
        if self.cancellable and not self.too_late_to_cancel:
            self.cancellable.cancel()
