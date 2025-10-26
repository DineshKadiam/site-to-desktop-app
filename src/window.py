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
from .url_dialog import URLDialog


class WebAppsWindow(Adw.ApplicationWindow):
    __gtype_name__ = "WebAppsWindow"

    def __init__(self, application, **kwargs):
        super().__init__(application=application)
        self.app = application
        self.set_default_size(800, 600)
        self.set_size_request(360, 294)
        self.set_default_icon_name("net.codelogistics.webapps")
        self.set_title(_("Web Apps"))

        application.create_action(
            "close_mainwindow", lambda *_: self.close(), ["<primary>w"]
        )

        toolbar = Adw.ToolbarView.new()
        toolbar.set_halign(Gtk.Align.FILL)
        toolbar.set_hexpand(True)

        headerbar = Adw.HeaderBar.new()

        window_title = Adw.WindowTitle.new()
        window_title.set_title(_("Web Apps"))
        headerbar.set_title_widget(window_title)

        add_button = Gtk.Button.new()
        add_button.set_icon_name("list-add-symbolic")
        add_button.connect("clicked", self.on_add_button_clicked, application)
        add_button.set_tooltip_text(_("Add Web App"))
        headerbar.pack_start(add_button)
        application.create_action(
            "new-app",
            lambda *_: self.on_add_button_clicked(add_button, application),
            ["<primary>n"],
        )

        menu_button = Gtk.MenuButton.new()
        menu_button.set_tooltip_text(_("Main Menu"))
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_primary(True)
        menu_button_menu = Gio.Menu.new()
        menu_button.set_menu_model(menu_button_menu)
        about_item = Gio.MenuItem.new(_("About"), "app.about")
        menu_button_menu.append_item(about_item)
        application.create_action(
            "report", lambda *_: self.on_report_broken(app=application)
        )
        report_button = Gio.MenuItem.new(_("Report Broken Website"), "app.report")
        menu_button_menu.append_item(report_button)
        headerbar.pack_end(menu_button)

        toolbar.add_top_bar(headerbar)

        self.box = Gtk.Box.new()
        self.box.set_hexpand(True)
        self.box.set_halign(Gtk.Align.FILL)

        self.scrolled = Gtk.ScrolledWindow.new()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_valign(Gtk.Align.FILL)
        self.scrolled.set_halign(Gtk.Align.FILL)
        self.scrolled.set_hexpand(True)

        self.clamp = Adw.Clamp.new()
        self.clamp.set_margin_top(8)
        self.clamp.set_margin_bottom(8)
        self.clamp.set_margin_start(32)
        self.clamp.set_margin_end(32)

        rowbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL)
        rowbox.set_margin_bottom(8)
        heading = Gtk.Label.new(label=_("Your Web Apps"))
        heading.add_css_class("heading")
        heading.set_halign(Gtk.Align.START)
        rowbox.append(heading)
        heading.set_margin_bottom(8)

        self.apps_list = Gtk.ListBox.new()
        self.apps_list.add_css_class("boxed-list")
        self.apps_list.set_selection_mode(Gtk.SelectionMode.NONE)
        rowbox.append(self.apps_list)
        self.clamp.set_child(rowbox)
        self.scrolled.set_child(self.clamp)

        self.no_webapps_page = Adw.StatusPage.new()
        self.no_webapps_page.set_hexpand(True)
        self.no_webapps_page.set_vexpand(True)
        self.no_webapps_page.set_title(_("No Web Apps installed"))
        self.no_webapps_page.set_description(
            _("Press the Add Web App button to create one")
        )
        self.no_webapps_page.set_icon_name("web-browser-symbolic")

        if (
            len(os.listdir(".var/app/net.codelogistics.webapps/webapps/")) > 1
        ):  # uuid_verified is always there.
            self.box.append(self.scrolled)

        else:
            self.box.append(self.no_webapps_page)

        toolbar.set_content(self.box)

        self.set_content(toolbar)

        self.rows = self.add_rows(self.apps_list, application)

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
        try:
            self.box.remove(self.no_webapps_page)
            self.box.append(self.scrolled)

        except:
            pass

        for i in self.rows:
            self.apps_list.remove(self.rows[i])
        self.rows = self.add_rows(self.apps_list)
        if self.rows == {}:
            self.box.remove(self.scrolled)
            self.box.append(self.no_webapps_page)

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
        def submit(button):
            title = "[Bug][Auto-generated]+" + url_entry.get_text() + "+broken"
            body = ""
            if app_creation_radio.get_active():
                body += "Cannot install the website " + url_entry.get_text()
            elif website_broken_radio.get_active():
                body += "Website+" + url_entry.get_text() + "+broken"

            body += "%0A%0A**Distro:**%0A**Version:**%0A**Desktop environment:**%0A**Version:**%0A%0A**Details (in English):**%0A%0A"
            os.system(
                'xdg-open "https://codeberg.org/eyekay/webapps/issues/new?title='
                + title
                + "&body="
                + body
                + '"'
            )

            broken_dialog.close()

        broken_dialog = Adw.Dialog.new()
        broken_dialog.set_title(_("Report Broken Website"))
        broken_dialog.set_content_width(500)
        broken_dialog.set_content_height(300)

        toolbar = Adw.ToolbarView.new()
        headerbar = Adw.HeaderBar.new()

        clamp = Adw.Clamp.new()
        box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL)
        box.set_valign(Gtk.Align.CENTER)

        label = Gtk.Label.new()
        label.set_markup(_("Website broken?"))
        label.add_css_class("title-1")
        label.set_margin_bottom(8)
        box.append(label)

        url_entry = Gtk.Entry.new()
        url_entry.set_hexpand(True)
        url_entry.set_placeholder_text(_("Enter URL"))
        url_entry.set_margin_bottom(8)
        box.append(url_entry)

        app_creation_radio = Gtk.CheckButton.new()
        app_creation_radio.set_active(True)
        app_creation_radio.set_label(_("I can't install the website"))
        box.append(app_creation_radio)

        website_broken_radio = Gtk.CheckButton.new()
        website_broken_radio.set_group(app_creation_radio)
        website_broken_radio.set_label(_("The website is not opening/ working"))
        website_broken_radio.set_margin_bottom(8)
        box.append(website_broken_radio)

        submit_button = Gtk.Button.new()
        submit_button.set_vexpand(False)
        submit_button.set_label(_("Submit"))
        submit_button.connect("clicked", submit)
        submit_button.set_tooltip_text(_("Submit"))
        submit_button.add_css_class("suggested-action")
        submit_button.add_css_class("pill")
        box.append(submit_button)

        clamp.set_child(box)

        toolbar.set_content(clamp)

        toolbar.add_top_bar(headerbar)
        broken_dialog.set_child(toolbar)
        broken_dialog.present(self)
