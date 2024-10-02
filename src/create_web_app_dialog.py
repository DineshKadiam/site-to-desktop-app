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
import gi
import uuid

from gi.repository import Gtk, Gio, Adw, Gdk, GdkPixbuf

from .web_app_properties import WebAppProperties
from .create_desktop_file import desktop_filer

class CreateWebAppDialog(Adw.Dialog):

    def __init__(self, parent_window, state, **kwargs):
        super().__init__()

        self.parent_window = parent_window

        self.set_title(_("Add Web App"))
        self.set_content_width(500)
        self.set_content_height(800)

        toolbar = Adw.ToolbarView()

        headerbar = Adw.HeaderBar()

        self.add_button = Gtk.Button()
        self.add_button.add_css_class("suggested-action")
        self.add_button.set_sensitive(False)
        self.add_button.set_label(_("Install"))
        self.add_button.set_tooltip_text(_("Create a new web app"))

        headerbar.pack_end(self.add_button)

        toolbar.add_top_bar(headerbar)

        scrolled = Gtk.ScrolledWindow()
        properties = WebAppProperties(edit=False, state=state, parent_window = parent_window)
        scrolled.set_child(properties)
        toolbar.set_content(scrolled)
        self.set_child(toolbar)

        properties.name_row.connect("changed", self.enable_install)
        self.add_button.connect("clicked", self.install_webapp, [properties.name_row, properties.url_row, properties.avatar, properties.show_navigation_row, properties.domain_matching_row, properties.loading_bar_row, properties.javascript_row, properties.incognito_row, properties.user_agent_row])
        self.enable_install(properties.name_row)

    def enable_install(self, entry):
        if entry.get_text().strip() == "":
            self.add_button.set_sensitive(False)
        else:
            self.add_button.set_sensitive(True)

    def install_webapp(self, button, widgets):

        app_id = 'webapp-' + str(uuid.uuid4())

        icon_path = '.var/app/net.codelogistics.webapps/icons/192x192/net.codelogistics.webapps.' + app_id + '.png'
        paintable = widgets[2].draw_to_texture(1)
        paintable.save_to_png(icon_path)

        if widgets[1].get_text() == "":
            url = "about:blank"
        else:
            url = widgets[1].get_text()
        if not url.startswith('http'):
            url = 'https://' + url

        state = {
            'app_id': app_id,
            'name': widgets[0].get_text(),
            'url': url,
            'icon': icon_path,
            'show_navigation': widgets[3].get_active(),
            'domain_matching': widgets[4].get_selected(),
            'loading_bar': widgets[5].get_active(),
            'javascript': widgets[6].get_active(),
            'incognito': widgets[7].get_active(),
            'user_agent': widgets[8].get_text()
        }

        with open('.var/app/net.codelogistics.webapps/webapps/' + state['app_id'] + '.json', 'w') as f:
            json.dump(state, f)

        desktop_filer(self.parent_window, state['app_id'], state['name'])

        self.close()

        self.parent_window.refresh_rows()
