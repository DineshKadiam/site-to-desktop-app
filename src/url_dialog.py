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


class URLDialog(Adw.Dialog):
    def __init__(self, parent_window, app):
        super().__init__()

        self.app = app
        self.parent_window = parent_window

        self.set_content_width(500)
        self.set_content_height(600)
        self.set_title(_("Add Web App"))

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text(_("Enter URL…"))
        self.url_entry.connect("changed", self.enable_add_button)
        self.url_entry.set_activates_default(True)

        self.add_button = Gtk.Button()
        self.add_button.set_sensitive(False)
        self.add_button.set_vexpand(False)
        self.add_button.set_halign(Gtk.Align.CENTER)
        self.add_button.set_label(_("Add"))
        self.add_button.connect("clicked", self.add_webapp)
        self.add_button.set_tooltip_text(_("Add"))
        self.add_button.add_css_class("suggested-action")
        self.add_button.add_css_class("pill")
        self.set_default_widget(self.add_button)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, spacing=12)
        box.set_vexpand(True)
        box.set_hexpand(True)
        box.append(self.url_entry)
        box.append(self.add_button)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(300)
        clamp.set_child(box)

        status_page = Adw.StatusPage.new()
        status_page.set_title(_("Enter URL"))
        status_page.set_description(_("Enter the URL of the Web App you want to add"))
        status_page.set_icon_name("search-global")
        status_page.set_vexpand(True)
        status_page.set_hexpand(True)
        status_page.set_child(clamp)

        spinner = Adw.Spinner.new()
        spinner.set_size_request(50, 50)

        self.stack = Gtk.Stack()
        self.stack.add_named(status_page, "clamp")
        self.stack.add_named(spinner, "loading")

        toolbar_view = Adw.ToolbarView()
        toolbar_view.set_content(self.stack)
        toolbar_view.add_top_bar(Adw.HeaderBar.new())
        self.set_child(toolbar_view)

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
