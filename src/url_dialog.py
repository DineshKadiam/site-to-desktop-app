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
import json
import shutil

gi.require_version("Adw", '1')

from gi.repository import Gtk, Adw, GLib, Gio

from .parse_manifest import get_website_data_from_manifest
from .parse_webpage import get_website_data_from_webpage

class URLDialog(Adw.Dialog):
    def __init__(self, parent_window, app):
        super().__init__()

        self.app = app
        self.parent_window = parent_window

        self.set_title("Enter URL")

        self.set_title(_("Add Web App"))
        self.set_content_width(500)
        self.set_content_height(300)

        toolbar = Adw.ToolbarView()
        headerbar = Adw.HeaderBar()

        self.stack = Gtk.Stack()

        clamp = Adw.Clamp()
        clamp.set_maximum_size(275)
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        box.set_valign(Gtk.Align.CENTER)

        label = Gtk.Label()
        label.set_markup(_("Enter URL"))
        label.add_css_class("title-1")
        box.append(label)
        label.set_margin_bottom(8)
        
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text(_("Enter URL"))
        self.url_entry.connect("changed", self.enable_add_button)
        box.append(self.url_entry)
        self.url_entry.set_margin_bottom(8)

        self.add_button = Gtk.Button()
        self.add_button.set_sensitive(False)
        self.add_button.set_vexpand(False)
        self.add_button.set_halign(Gtk.Align.CENTER)
        self.add_button.set_label(_("Add"))
        self.add_button.connect("clicked", self.add_webapp)
        self.add_button.set_tooltip_text(_("Add"))
        self.add_button.add_css_class("suggested-action")
        self.add_button.add_css_class("pill")
        app.create_action('add_webapp', self.add_webapp, ['Return'])
        box.append(self.add_button)

        clamp.set_child(box)

        self.stack.add_named(clamp, "clamp")

        loading_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        loading_box.set_vexpand(True)
        loading_box.set_valign(Gtk.Align.CENTER)

        spinner = Gtk.Spinner()
        spinner.set_vexpand(True)
        spinner.set_valign(Gtk.Align.CENTER)
        spinner.start()
        loading_box.append(spinner)

        self.stack.add_named(loading_box, "loading")
        toolbar.set_content(self.stack)

        toolbar.add_top_bar(headerbar)
        self.set_child(toolbar)

        self.cancellable = None
        self.too_late_to_cancel = False
        
        self.connect("closed", self.cancelled)

    def enable_add_button(self, entry):
        test_url = entry.get_text()
        if test_url.strip() != "" and test_url.find(" ") == -1:
            if (test_url.find(".") != -1 and len(test_url.rpartition(".")[-1]) >= 2) or ((test_url.startswith("http://") or test_url.startswith("https://")) and len(test_url[test_url.find("://")+3:]) >= 1):
                self.add_button.set_sensitive(True)
                return

        self.add_button.set_sensitive(False)

    def add_webapp(self, button, data = None):
        if not self.add_button.get_sensitive(): # for the shortcut
            return

        self.stack.set_visible_child_name("loading")

        GLib.idle_add(self.get_data)

    def get_data(self):
        url = self.url_entry.get_text()
        self.cancellable = Gio.Cancellable()
        manifest_data = get_website_data_from_manifest(self, url, self.cancellable)
        # this is an async function, it will call gotten_manifest_data()

    def gotten_manifest_data(self, name, url, favicon, cancellable):
        if not cancellable.is_cancelled():
            if name == None or favicon == None:
                # manifest not found
                website_data = get_website_data_from_webpage(self, url, cancellable)
                # this is an async function, it will call gotten_website_data()
            else:
                state = {'name': name, 'url': url, 'icon': favicon}
                self.parent_window.show_create_window(self, state)
                self.add_button.set_sensitive(False)

    def gotten_website_data(self, name, url, favicon, cancellable):
        if not cancellable.is_cancelled():
            if name == None:
                # title not found by html parser
                name = _("New Web App")
            if favicon == None:
                favicon = '/tmp/tmp_webapps_icon.png'

            state = {'name': name, 'url': url, 'icon': favicon}
            self.parent_window.show_create_window(self, state)
            self.add_button.set_sensitive(False)

    def cancelled(self, dialog):
        if self.cancellable and not self.too_late_to_cancel:
            self.cancellable.cancel()
