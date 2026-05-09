# window.py
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


import shutil

import gi

gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from . import web_app_paths as paths
from .create_desktop_file import name_desktop_file, uninstall_desktop_file
from .create_web_app_dialog import CreateWebAppDialog
from .edit_web_app_dialog import EditWebAppDialog
from .report_broken_dialog import ReportBrokenDialog
from .url_dialog import URLDialog
from .web_app_state import load_state, states


@Gtk.Template(resource_path="/net/codelogistics/webapps/window.ui")
class WebAppsWindow(Adw.ApplicationWindow):
    __gtype_name__ = "WebAppsWindow"

    add_button = Gtk.Template.Child()
    apps_list = Gtk.Template.Child()
    stack = Gtk.Template.Child()

    def __init__(self, application, **kwargs):
        super().__init__(application=application)
        self.app = application

        application.create_action(
            "close_mainwindow", lambda *_: self.close(), ["<primary>w"]
        )

        self.add_button.connect("clicked", self.on_add_button_clicked, application)
        application.create_action(
            "new-app",
            lambda *_: self.on_add_button_clicked(self.add_button, application),
            ["<primary>n"],
        )

        application.create_action(
            "report", lambda *_: self.on_report_broken(app=application)
        )

        self.rows = self.add_rows(self.apps_list, application)
        self.refresh_rows()  # Ensure correct initial state

    def on_add_button_clicked(self, button, app):
        URLDialog(self, app).present(parent=self)

    def show_create_window(self, urldialog, state, invalid=False):
        create_app_dialog = CreateWebAppDialog(
            parent_window=self, state=state, invalid=invalid
        )
        create_app_dialog.present(self)

        urldialog.too_late_to_cancel = True
        urldialog.close()

    def add_rows(self, apps_list, application=None):
        rows = {}
        for tmpstate in states():
            app_id = tmpstate["app_id"]

            row = Adw.ActionRow.new()
            row.set_title(tmpstate["name"])
            row.set_title_lines(1)

            edit_btn = Gtk.Button.new()
            edit_btn.add_css_class("flat")
            edit_btn.set_icon_name("document-edit-symbolic")
            edit_btn.set_tooltip_text(_("Edit"))
            edit_btn.connect("clicked", self.edit_row, app_id)
            edit_btn.set_vexpand(False)
            edit_btn.set_valign(Gtk.Align.CENTER)
            row.add_suffix(edit_btn)

            delete_btn = Gtk.Button.new()
            delete_btn.add_css_class("flat")
            delete_btn.set_icon_name("user-trash-symbolic")
            delete_btn.set_tooltip_text(_("Delete"))
            delete_btn.connect("clicked", self.delete_row, app_id)
            delete_btn.set_vexpand(False)
            delete_btn.set_valign(Gtk.Align.CENTER)
            row.add_suffix(delete_btn)

            rows[app_id] = row

            apps_list.append(rows[app_id])

        return rows

    def refresh_rows(self):
        for i in self.rows:
            self.apps_list.remove(self.rows[i])
        self.rows = self.add_rows(self.apps_list)

        if self.rows == {}:
            self.stack.set_visible_child_name("empty")
        else:
            self.stack.set_visible_child_name("list")

    def delete_row(self, button, app_id):
        aux_app_files = [
            paths.app_window_state(app_id),
            paths.app_webkitgtk_cookies(app_id),
            paths.app_icon_file(app_id),
        ]
        for aux in aux_app_files:
            aux.unlink(missing_ok=True)

        webkitgtk_dirs = [
            paths.app_webkitgtk_cache(app_id),
            paths.app_webkitgtk_data(app_id),
        ]
        for dir in webkitgtk_dirs:
            if dir.exists():
                shutil.rmtree(dir)

        uninstall_desktop_file(name_desktop_file(app_id))

        cache_dir = paths.app_cache_dir(app_id)
        if cache_dir.exists():
            cache_dir.rmdir()

        paths.app_state(app_id).unlink()
        paths.app_data_dir(app_id).rmdir()
        self.refresh_rows()

    def edit_row(self, button, app_id):
        EditWebAppDialog(self, state=load_state(app_id), app=self.app).present(
            parent=self
        )

    def on_report_broken(self, app):
        ReportBrokenDialog().present(self)
