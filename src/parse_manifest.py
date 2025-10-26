# parse_manifest.py
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
import time
from urllib import parse

import gi

gi.require_version("Soup", "3.0")
from gi.repository import GLib, Soup

from .manifest_html_parser import ManifestHTMLParser


def get_website_data_from_manifest(dialog, url, cancellable):
    """Get the favicon and name from the given url through the manifest, if any."""

    def check_if_data():
        if favicon or time.time() >= end_time or giveup:
            dialog.gotten_manifest_data(name, url, favicon, cancellable)
            return False
        return True

    if not url.startswith("http"):
        url = "https://" + url
    if not url.endswith("/"):
        url += "/"

    name = None
    favicon = None
    giveup = False

    try:

        def got_message(session, result, error=None):
            nonlocal name
            nonlocal favicon
            nonlocal giveup
            try:
                html = str(session.send_and_read_finish(result).get_data())
            except:
                giveup = True
                return False
            parser = ManifestHTMLParser()
            parser.feed(html)
            manifest_url = parser.manifest_url

            if manifest_url:
                if not (
                    manifest_url.startswith("http")
                    or manifest_url.startswith("data:application/json")
                ):
                    # this is a relative path
                    domain_name = parse.urlparse(url).netloc
                    manifest_prefix = (
                        manifest_url.rpartition("/")[0] + "/"
                        if manifest_url.rpartition("/")[0] != ""
                        else ""
                    )
                    # sometimes manifest urls are in form of images/manifest.json etc
                    manifest_url = (
                        "https://" + domain_name + "/" + manifest_url.lstrip("/")
                    )
                else:
                    manifest_prefix = ""

                try:

                    def got_manifest_message(session, result, error=None):
                        nonlocal name
                        nonlocal favicon
                        nonlocal giveup
                        data = (
                            session.send_and_read_finish(result)
                            .get_data()
                            .decode("utf-8")
                        )
                        try:
                            manifest = json.loads(data)
                        except Exception:
                            giveup = True
                            return

                        if "name" in manifest:
                            name = manifest["name"]

                        if "icons" in manifest:
                            max_size = [0, ""]
                            for i in manifest["icons"]:
                                if "purpose" in i and i["purpose"] == "monochrome":
                                    continue
                                size = int(i["sizes"].split("x")[0])
                                if size > max_size[0] and size <= 512:
                                    max_size = [size, i["src"]]
                                if "type" in i and (
                                    i["type"] == "image/svg"
                                    or i["type"] == "image/svg+xml"
                                ):
                                    max_size = [512, i["src"]]

                            if (
                                max_size[1] == ""
                            ):  # We only want icons upto 512x512 in size otherwise the dynamic launcher breaks.
                                giveup = True
                                return None

                            if not max_size[1].startswith("http"):
                                max_size[1] = (
                                    "https://"
                                    + domain_name
                                    + "/"
                                    + manifest_prefix
                                    + max_size[1].lstrip("/")
                                )

                            try:

                                def got_favicon_message(session, result, error=None):
                                    nonlocal favicon
                                    icon = session.send_and_read_finish(
                                        result
                                    ).get_data()
                                    with open("/tmp/webapps_icon.png", "wb") as f:
                                        f.write(icon)

                                    favicon = "/tmp/webapps_icon.png"

                                favicon_message = Soup.Message.new("GET", max_size[1])
                                session.send_and_read_async(
                                    favicon_message, 1, cancellable, got_favicon_message
                                )
                            except:
                                giveup = True
                                return None

                        else:
                            giveup = True

                    manifest_message = Soup.Message.new("GET", manifest_url)
                    session.send_and_read_async(
                        manifest_message, 1, cancellable, got_manifest_message
                    )
                except:
                    giveup = True

            else:
                giveup = True

        session = Soup.Session()
        session.set_timeout(5)
        message = Soup.Message.new("GET", url)
        session.send_and_read_async(message, 1, cancellable, got_message)
    except Exception as e:
        print(_("Error accessing URL:"), e)

    end_time = time.time() + 5
    GLib.timeout_add(200, check_if_data)
