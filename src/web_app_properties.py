# web_app_properties.py
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

import shutil

import gi

gi.require_version("WebKit", "6.0")
from gi.repository import Adw, Gdk, Gio, Gtk, WebKit


@Gtk.Template(resource_path="/net/codelogistics/webapps/web_app_properties.ui")
class WebAppProperties(Adw.Bin):
    __gtype_name__ = "WebAppProperties"

    avatar = Gtk.Template.Child()
    select_icon_button = Gtk.Template.Child()
    name_row = Gtk.Template.Child()
    url_row = Gtk.Template.Child()
    show_navigation_row = Gtk.Template.Child()
    domain_matching_row = Gtk.Template.Child()
    loading_bar_row = Gtk.Template.Child()
    javascript_row = Gtk.Template.Child()
    incognito_row = Gtk.Template.Child()
    user_agent_row = Gtk.Template.Child()

    def __init__(self, edit=False, state=False, parent_window=None):
        super().__init__()
        self.parent_window = parent_window

        self.avatar.set_text(state["name"])
        self.select_icon_button.connect("clicked", self.choose_icon)

        if edit:
            self.name_row.set_sensitive(False)
        if edit or (state and state["name"] != ""):
            self.name_row.set_text(state["name"])
        self.name_row.connect("changed", self.on_name_changed)

        if state:
            self.url_row.set_text(state["url"])

        if edit:
            self.show_navigation_row.set_active(state["show_navigation"])
            self.domain_matching_row.set_selected(state["domain_matching"])
            self.loading_bar_row.set_active(state["loading_bar"])
            self.javascript_row.set_active(state["javascript"])
            self.incognito_row.set_active(state["incognito"])

        webkit_settings = WebKit.Settings.new()
        user_agent = webkit_settings.get_user_agent()
        del webkit_settings
        self.user_agent_row.set_text(user_agent)
        if state and "user_agent" in state:
            self.user_agent_row.set_text(state["user_agent"])

        if state["icon"] == "/tmp/tmp_webapps_icon.png":
            return
        try:
            texture = Gdk.Texture.new_from_file(
                Gio.File.new_for_path(str(state["icon"]))
            )
            self.avatar.set_custom_image(texture)
        except Exception as e:
            print(e)

    def on_name_changed(self, row):
        self.avatar.set_text(row.get_text())

    def choose_icon(self, button):
        choose_dialog = Gtk.FileDialog.new()

        def choose_icon_finish(dialog, result):
            selected_icon = choose_dialog.open_finish(result).get_path()
            icon_path = "/tmp/webapps_icon.png"
            shutil.copyfile(selected_icon, icon_path)
            texture = Gdk.Texture.new_from_file(
                Gio.File.new_for_path("/tmp/webapps_icon.png")
            )
            self.avatar.set_custom_image(texture)

        pngfilter = Gtk.FileFilter.new()
        pngfilter.set_name("PNG")
        pngfilter.add_suffix("png")
        choose_dialog.set_default_filter(pngfilter)
        choose_dialog.open(self.parent_window, None, choose_icon_finish)
