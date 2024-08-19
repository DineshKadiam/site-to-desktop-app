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

import os
import gi
import shutil

gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Gdk, Gio, Adw, WebKit

class WebAppProperties(Adw.Bin):
    def __init__(self, edit = False, state = False, parent_window = None):
        super().__init__()
        self.parent_window = parent_window

        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        box.set_halign(Gtk.Align.CENTER)
        
        self.avatar = Adw.Avatar()
        self.avatar.set_size(128)
        self.avatar.set_show_initials(True)
        self.avatar.set_text(state['name'])
        box.append(self.avatar)

        select_icon_button = Gtk.Button()
        select_icon_button.set_hexpand(False)
        select_icon_button.set_halign(Gtk.Align.CENTER)
        select_icon_button.add_css_class('flat')
        button_content = Adw.ButtonContent()
        button_content.set_label(_("Browse Icon"))
        button_content.set_icon_name("folder-open-symbolic")
        select_icon_button.set_child(button_content)
        select_icon_button.connect("clicked", self.choose_icon)
        select_icon_button.set_margin_bottom(8)
        box.append(select_icon_button)

        prefs_clamp = Adw.Clamp()
        prefs_list = Gtk.ListBox()
        prefs_list.add_css_class("boxed-list")
        prefs_list.set_selection_mode(Gtk.SelectionMode.NONE)

        self.name_row = Adw.EntryRow()
        self.name_row.set_title(_("Name"))
        if edit:
            self.name_row.set_sensitive(False)
        if edit or (state and state['name'] != ''):
            self.name_row.set_text(state['name'])
        self.name_row.connect("changed", lambda row: self.avatar.set_text(row.get_text()))
        prefs_list.append(self.name_row)

        self.url_row = Adw.EntryRow()
        self.url_row.set_title(_("URL"))
        if state:
            self.url_row.set_text(state['url'])
        prefs_list.append(self.url_row)

        self.show_navigation_row = Adw.SwitchRow()
        self.show_navigation_row.set_title(_("Show Navigation Options"))
        self.show_navigation_row.set_subtitle(_("Show the buttons for back, forward and reload."))
        if edit:
            self.show_navigation_row.set_active(state['show_navigation'])
        prefs_list.append(self.show_navigation_row)

        self.domain_matching_row = Adw.ComboRow()
        self.domain_matching_row.set_title(_("Domain Matching"))
        self.domain_matching_row.set_subtitle(_("Set which websites will be allowed to load in the web app."))
        domain_options = Gtk.StringList()
        domain_options.append(_("Domain and subdomains"))
        domain_options.append(_("Domain only"))
        domain_options.append(_("Allow all"))
        self.domain_matching_row.set_model(domain_options)
        if edit:
            self.domain_matching_row.set_selected(state['domain_matching'])
        prefs_list.append(self.domain_matching_row)

        self.loading_bar_row = Adw.SwitchRow()
        self.loading_bar_row.set_title(_("Show Loading Bars"))
        self.loading_bar_row.set_subtitle(_("A loading bar will be visible at the top of the web page when it is being loaded."))
        self.loading_bar_row.set_active(True)
        if edit:
            self.loading_bar_row.set_active(state['loading_bar'])
        prefs_list.append(self.loading_bar_row)

        self.javascript_row = Adw.SwitchRow()
        self.javascript_row.set_title(_("Enable JavaScript"))
        self.javascript_row.set_subtitle(_("Enable web scripting."))
        self.javascript_row.set_active(True)
        if edit:
            self.javascript_row.set_active(state['javascript'])
        prefs_list.append(self.javascript_row)

        self.incognito_row = Adw.SwitchRow()
        self.incognito_row.set_title(_("Incognito Browsing"))
        self.incognito_row.set_subtitle(_("Cookies and other data will not be stored."))
        if edit:
            self.incognito_row.set_active(state['incognito'])
        prefs_list.append(self.incognito_row)

        webkit_settings = WebKit.Settings()
        user_agent = webkit_settings.get_user_agent()
        del(webkit_settings)
        self.user_agent_row = Adw.EntryRow()
        self.user_agent_row.set_title(_("User Agent"))
        self.user_agent_row.set_text(user_agent)
        if state and 'user_agent' in state:
            self.user_agent_row.set_text(state['user_agent'])
        prefs_list.append(self.user_agent_row)

        prefs_clamp.set_child(prefs_list)
        box.append(prefs_clamp)
        prefs_clamp.set_margin_bottom(8)
        self.set_child(box)

        if not state['icon'] == '/tmp/tmp_webapps_icon.png':
            texture = None
            try:
                texture = Gdk.Texture.new_from_file(Gio.File.new_for_path(state['icon']))
            except Exception as e:
                print(e)
            if texture:
                self.avatar.set_custom_image(texture)

    def choose_icon(self, button):
        def choose_icon_finish(dialog, result):
            selected_icon = choose_dialog.open_finish(result).get_path()
            icon_path = '/tmp/webapps_icon.png'
            shutil.copyfile(selected_icon, icon_path)
            texture = Gdk.Texture.new_from_file(Gio.File.new_for_path('/tmp/webapps_icon.png'))
            self.avatar.set_custom_image(texture)

        choose_dialog = Gtk.FileDialog()
        pngfilter = Gtk.FileFilter()
        pngfilter.set_name("PNG")
        pngfilter.add_suffix("png")
        choose_dialog.set_default_filter(pngfilter)
        choose_dialog.open(self.parent_window, None, choose_icon_finish)
