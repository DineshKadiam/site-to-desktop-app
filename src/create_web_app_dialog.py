# create_web_app_dialog.py
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

import json
import uuid

from gi.repository import Adw, Gtk

from .create_desktop_file import desktop_filer
from .web_app_properties import WebAppProperties


@Gtk.Template(resource_path="/net/codelogistics/webapps/create_web_app_dialog.ui")
class CreateWebAppDialog(Adw.Dialog):
    __gtype_name__ = "CreateWebAppDialog"

    add_button = Gtk.Template.Child()
    invalid_banner = Gtk.Template.Child()
    content_scrolled = Gtk.Template.Child()

    def __init__(self, parent_window, state, invalid=False, **kwargs):
        super().__init__()

        self.parent_window = parent_window

        if invalid:
            self.invalid_banner.set_revealed(True)

        self.properties = WebAppProperties(
            edit=False, state=state, parent_window=parent_window
        )
        self.content_scrolled.set_child(self.properties)

        self.properties.name_row.connect("changed", self.enable_install)
        self.add_button.connect("clicked", self.install_webapp)
        self.enable_install(self.properties.name_row)

    def enable_install(self, entry):
        self.add_button.set_sensitive(entry.get_text().strip() != "")

    def install_webapp(self, button):
        app_id = "webapp_" + str(uuid.uuid4()).replace("-", "_")

        icon_path = (
            ".var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps."
            + app_id
            + ".png"
        )
        paintable = self.properties.avatar.draw_to_texture(1)
        paintable.save_to_png(icon_path)

        text = self.properties.url_row.get_text()
        url = text if text != "" else "about:blank"
        if not url.startswith("http"):
            url = "https://" + url

        state = {
            "app_id": app_id,
            "name": self.properties.name_row.get_text(),
            "url": url,
            "icon": icon_path,
            "show_navigation": self.properties.show_navigation_row.get_active(),
            "domain_matching": self.properties.domain_matching_row.get_selected(),
            "loading_bar": self.properties.loading_bar_row.get_active(),
            "javascript": self.properties.javascript_row.get_active(),
            "incognito": self.properties.incognito_row.get_active(),
            "user_agent": self.properties.user_agent_row.get_text(),
        }

        with open(
            ".var/app/net.codelogistics.webapps/webapps/" + state["app_id"] + ".json",
            "w",
        ) as f:
            json.dump(state, f)

        desktop_filer(self.parent_window, state["app_id"], state["name"])

        self.close()
        self.parent_window.refresh_rows()
