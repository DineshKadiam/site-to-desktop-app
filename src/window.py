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

import json
import os

import gi

gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk

from .create_web_app_dialog import CreateWebAppDialog
from .edit_web_app_dialog import EditWebAppDialog
from .report_broken_dialog import ReportBrokenDialog
from .url_dialog import URLDialog

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
        for i in os.listdir(".var/app/net.codelogistics.webapps/webapps/"):
            if i.endswith(".json") and not i.endswith(".permissions.json"):
                with open(".var/app/net.codelogistics.webapps/webapps/" + i, "r") as f:
                    try:
                        tmpstate = json.load(f)
                    except:
                        # Translators: Keep the {} as it is
                        print(
                            _("File {} broken! Maybe it was modified locally?").format(
                                i
                            )
                        )
                        continue

                row = Adw.ActionRow.new()
                row.set_title(tmpstate["name"])
                row.set_title_lines(1)

                edit_btn = Gtk.Button.new()
                edit_btn.add_css_class("flat")
                edit_btn.set_icon_name("document-edit-symbolic")
                edit_btn.set_tooltip_text(_("Edit"))
                edit_btn.connect("clicked", self.edit_row, i[:-5])
                edit_btn.set_vexpand(False)
                edit_btn.set_valign(Gtk.Align.CENTER)
                row.add_suffix(edit_btn)

                delete_btn = Gtk.Button.new()
                delete_btn.add_css_class("flat")
                delete_btn.set_icon_name("user-trash-symbolic")
                delete_btn.set_tooltip_text(_("Delete"))
                delete_btn.connect("clicked", self.delete_row, i[:-5])
                delete_btn.set_vexpand(False)
                delete_btn.set_valign(Gtk.Align.CENTER)
                row.add_suffix(delete_btn)

                rows[i] = row

                apps_list.append(rows[i])

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
        os.remove(".var/app/net.codelogistics.webapps/webapps/" + app_id + ".json")
        if os.path.exists(
            ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".window"
        ):
            os.remove(
                ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".window"
            )
        if os.path.exists(
            ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".cookies.txt"
        ):
            os.remove(
                ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".cookies.txt"
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
        if os.path.exists(
            ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".permissions.json"
        ):
            os.remove(
                ".var/app/net.codelogistics.webapps/webapps/"
                + app_id
                + ".permissions.json"
            )
        if os.path.exists(
            os.path.expanduser(
                "~/.local/share/applications/net.codelogistics.webapps."
                + app_id
                + ".desktop"
            )
        ):
            os.remove(
                os.path.expanduser(
                    "~/.local/share/applications/net.codelogistics.webapps."
                    + app_id
                    + ".desktop"
                )
            )
        self.refresh_rows()

    def edit_row(self, button, app_id):
        with open(
            ".var/app/net.codelogistics.webapps/webapps/" + app_id + ".json", "r"
        ) as f:
            tmpstate = json.load(f)
        EditWebAppDialog(self, state=tmpstate, app=self.app).present(parent=self)

    def on_report_broken(self, app):
        ReportBrokenDialog().present(self)
