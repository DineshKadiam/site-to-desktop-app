# report_broken_dialog.py
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

gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/net/codelogistics/webapps/report_broken_dialog.ui")
class ReportBrokenDialog(Adw.Dialog):
    __gtype_name__ = "ReportBrokenDialog"

    url_entry = Gtk.Template.Child()
    app_creation_radio = Gtk.Template.Child()
    website_broken_radio = Gtk.Template.Child()
    submit_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__()
        self.submit_button.connect("clicked", self.submit)

    def submit(self, button):
        title = "[Bug][Auto-generated]+" + self.url_entry.get_text() + "+broken"
        body = ""
        if self.app_creation_radio.get_active():
            body += "Cannot install the website " + self.url_entry.get_text()
        elif self.website_broken_radio.get_active():
            body += "Website+" + self.url_entry.get_text() + "+broken"

        body += "%0A%0A**Distro:**%0A**Version:**%0A**Desktop environment:**%0A**Version:**%0A%0A**Details (in English):**%0A%0A"
        os.system(
            'xdg-open "https://codeberg.org/eyekay/webapps/issues/new?title='
            + title
            + "&body="
            + body
            + '"'
        )

        self.close()
