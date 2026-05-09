# web_app_window.py
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

import os
from pathlib import Path
from urllib import parse

import gi

from . import web_app_paths as paths
from .web_app_paths import APP_ID
from .web_app_state import (
    load_permissions,
    load_window_state,
    save_permissions,
    save_window_state,
)

gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")

from gi.repository import Adw, GLib, Gtk, WebKit


@Gtk.Template(resource_path="/net/codelogistics/webapps/web_app_window.ui")
class WebAppWindow(Adw.ApplicationWindow):
    __gtype_name__ = "WebAppWindow"

    toolbar = Gtk.Template.Child()
    headerbar = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    forward_button = Gtk.Template.Child()
    reload_button = Gtk.Template.Child()
    hide_button = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    progressbar = Gtk.Template.Child()

    def __init__(self, application, state, **kwargs):
        super().__init__(application=application)
        name = state["name"]
        self.set_title(name)
        GLib.set_application_name(name)

        self.set_default_icon_name(APP_ID)
        self.connect("close-request", self.on_close, state)

        application.create_action(
            "close_webapp", lambda *_: self.close(), ["<primary>w"]
        )
        app_id = state["app_id"]

        network_session = WebKit.NetworkSession.new_ephemeral()
        if not state["incognito"]:
            data_dir = paths.app_webkitgtk_data(app_id)
            cache_dir = paths.app_webkitgtk_cache(app_id)

            network_session = WebKit.NetworkSession.new(str(data_dir), str(cache_dir))
            cookies = network_session.get_cookie_manager()
        self.webview = WebKit.WebView(network_session=network_session)
        settings = self.webview.get_settings()
        settings.set_enable_media_capabilities(True)
        settings.set_enable_encrypted_media(True)
        settings.set_enable_webrtc(True)

        if not state["javascript"]:
            settings.set_enable_javascript(False)

        if not state["incognito"]:
            storage = WebKit.CookiePersistentStorage.TEXT
            policy = WebKit.CookieAcceptPolicy.ALWAYS
            cookies.set_accept_policy(policy)
            cookies.set_persistent_storage(
                str(paths.app_webkitgtk_cookies(app_id)),
                storage,
            )

        self.webview.set_vexpand(True)
        if state["url"] == "":
            state["url"] = "about:blank"
        self.webview.load_uri(state["url"])

        self.toast_overlay.set_child(self.webview)

        if state["loading_bar"]:
            self.progressbar.set_visible(True)
        else:
            self.progressbar.set_visible(False)

        # Translators: this is for going back in the browser
        self.back_button.connect("clicked", lambda button: self.webview.go_back())
        application.create_action(
            "back", lambda *_: self.webview.go_back(), ["<alt>Left", "Back"]
        )

        # Translators: this is for going back in the browser
        self.forward_button.connect("clicked", lambda button: self.webview.go_forward())
        application.create_action(
            "forward", lambda *_: self.webview.go_forward(), ["<alt>Right", "Forward"]
        )

        self.reload_button.connect("clicked", self.on_reload_clicked)
        self.hide_button.connect("clicked", self.on_hide)

        if state["show_navigation"]:
            self.back_button.set_visible(True)
            self.forward_button.set_visible(True)
            self.reload_button.set_visible(True)
            self.hide_button.set_visible(True)
        else:
            self.back_button.set_visible(False)
            self.forward_button.set_visible(False)
            self.reload_button.set_visible(False)
            self.hide_button.set_visible(False)

        if state.get("user_agent"):
            settings.set_user_agent(state["user_agent"])

        self.webview.connect("load-changed", self.on_load_changed)
        self.webview.connect("notify::estimated-load-progress", self.on_load_progress)
        self.webview.connect(
            "create",
            lambda webview, nav_action: self.on_create(
                nav_action.get_request().get_uri(), state
            ),
        )
        self.webview.connect("context-menu", self.on_context_menu)
        self.webview.connect("decide-policy", self.on_decide_policy, state)
        self.webview.connect("permission-request", self.on_permission_request, state)
        self.connect("notify::fullscreened", lambda *_: self.on_fullscreen())

        session = self.webview.get_network_session()
        session.connect("download-started", self.on_download)

        application.create_action(
            "zoom-in",
            lambda *_: self.webview.set_zoom_level(self.webview.get_zoom_level() + 0.1),
            ["<ctrl>plus"],
        )
        application.create_action(
            "zoom-out",
            lambda *_: self.webview.set_zoom_level(self.webview.get_zoom_level() - 0.1),
            ["<ctrl>minus"],
        )
        application.create_action(
            "zoom-restore", lambda *_: self.webview.set_zoom_level(1), ["<ctrl>0"]
        )
        application.create_action(
            "reload", lambda *_: self.webview.reload(), ["<Control>r"]
        )
        application.create_action(
            "fullscreen", lambda *_: self.toggle_fullscreen(), ["F11"]
        )

        current_dir = Path(__file__).parent
        exceptions_file = current_dir / "exceptions.txt"
        self.exceptions = exceptions_file.read_text().splitlines()

        restore_window = load_window_state(app_id)
        if restore_window is not None:
            if restore_window[0] == "True":
                self.maximize()
            if len(restore_window) > 1:
                if len(restore_window[1].split("x")) == 2:
                    self.set_default_size(
                        int(restore_window[1].split("x")[0]),
                        int(restore_window[1].split("x")[1]),
                    )
                if len(restore_window) > 2 and restore_window[2]:
                    self.webview.set_zoom_level(float(restore_window[2]))
        else:
            save_window_state(
                app_id, self.is_maximized(), self.get_width(), self.get_height()
            )

    def on_reload_clicked(self, button):
        if button.get_icon_name() == "process-stop-symbolic":
            self.webview.stop_loading()
            self.reload_button.set_icon_name("view-refresh-symbolic")
            button.set_tooltip_text(_("Reload"))
            self.progressbar.set_visible(False)
        else:
            self.webview.reload()
            self.reload_button.set_icon_name("process-stop-symbolic")
            button.set_tooltip_text(_("Stop"))

    def on_load_progress(self, webview, progress):
        self.progressbar.set_fraction(webview.get_estimated_load_progress())

    def on_context_menu(self, webview, context_menu, hit_test_result):
        if hit_test_result.context_is_editable() and not (
            hit_test_result.context_is_image()
            or hit_test_result.context_is_link()
            or hit_test_result.context_is_media()
        ):
            return None
        return True

    def on_load_changed(self, webview, event):
        if event == WebKit.LoadEvent.STARTED:
            self.progressbar.set_visible(True)
            self.reload_button.set_icon_name("process-stop-symbolic")
            self.reload_button.set_tooltip_text(_("Stop"))
        elif event == WebKit.LoadEvent.FINISHED:
            self.progressbar.set_visible(False)
            self.reload_button.set_icon_name("view-refresh-symbolic")
            self.reload_button.set_tooltip_text(_("Reload"))
        self.back_button.set_sensitive(self.webview.can_go_back())
        self.forward_button.set_sensitive(self.webview.can_go_forward())

    def on_decide_policy(self, webview, decision, decision_type, state):
        if (
            decision_type == WebKit.PolicyDecisionType.RESPONSE
            or decision_type == WebKit.PolicyDecisionType.NEW_WINDOW_ACTION
        ):
            if decision_type == WebKit.PolicyDecisionType.RESPONSE:
                uri = decision.get_response().get_uri()
                content_type = (
                    decision.get_response().get_http_headers().get_content_type()
                )
            else:
                uri = decision.get_navigation_action().get_request().get_uri()
                content_type = (
                    decision.get_navigation_action()
                    .get_request()
                    .get_http_headers()
                    .get_content_type()
                )

            if (
                not self.domain_allowed(uri, state["url"], state["domain_matching"])
            ) or (not self.webview.can_show_mime_type(content_type[0])):
                os.system(f"xdg-open {uri}")
                self.toast_overlay.add_toast(
                    Adw.Toast.new(_("Link opened in system browser"))
                )
                decision.ignore()

    def on_create(self, uri, state):
        if self.domain_allowed(uri, state["url"], state["domain_matching"]):
            self.webview.load_uri(uri)

    def on_close(self, window, state):
        save_window_state(
            state["app_id"],
            self.is_maximized(),
            self.get_width(),
            self.get_height(),
            self.webview.get_zoom_level(),
        )
        self.webview.terminate_web_process()

    def domain_allowed(self, new_uri, uri, strict) -> bool:
        new_parsed_uri = parse.urlparse(new_uri)
        new_domain_name = new_parsed_uri.netloc

        parsed_uri = parse.urlparse(uri)
        domain_name = parsed_uri.netloc

        # These domains are called by websites frequently, so they are manually allowed.
        # This is not an elegant solution, but it works well enough for me to not care about the security implications.

        if new_domain_name in self.exceptions:
            return True

        if strict == 1:
            return new_domain_name == domain_name
        if strict == 2:
            return True
        return (
            new_domain_name.split(".")[-2] + "." + new_domain_name.split(".")[-1]
            == domain_name.split(".")[-2] + "." + domain_name.split(".")[-1]
        )

    def on_permission_request(self, webview, request, state):
        app_id = state["app_id"]

        def request_allow(permission):
            permissions = load_permissions(app_id)
            if permissions is None:
                permissions = {permission: False}

            if permissions.get(permission):
                request.allow()
                return

            def request_finish(dialog, result):
                try:
                    number = dialog.choose_finish(result)
                except:
                    number = -1
                if number == 0:
                    request.allow()
                    permissions[permission] = True
                    save_permissions(app_id, permissions)
                else:
                    assert not permissions[permission]
                    save_permissions(app_id, permissions)
                    request.deny()

            dialog = Gtk.AlertDialog.new()
            match permission:
                case "geolocation":
                    # Translators: {} is the url of the website and it is necessary!
                    dialog.set_message(
                        _("Allow {} access to your location?").format(state["url"])
                    )
                case "notification":
                    # Translators: {} is the url of the website and it is necessary!
                    dialog.set_message(
                        _("Allow {} to send notifications?").format(state["url"])
                    )
                case "drm":
                    # Translators: {} is the url of the website and it is necessary!
                    dialog.set_message(
                        _("Allow {} to install and use DRM?").format(state["url"])
                    )
                case "clipboard":
                    # Translators: {} is the url of the website and it is necessary!
                    dialog.set_message(
                        _("Allow {} to access your clipboard?").format(state["url"])
                    )
                case "user_media":
                    # Translators: {} is the url of the website and it is necessary!
                    dialog.set_message(
                        _("Allow {} to access your microphone and/or camera?").format(
                            state["url"]
                        )
                    )
            dialog.set_buttons([_("Yes"), _("No")])
            dialog.choose(self, None, request_finish)

        match type(request):
            case WebKit.NotificationPermissionRequest:
                request_allow("notification")
            case WebKit.GeolocationPermissionRequest:
                request_allow("geolocation")
            case WebKit.MediaKeySystemPermissionRequest:
                request_allow("drm")
            case WebKit.ClipboardPermissionRequest:
                request_allow("clipboard")
            case WebKit.UserMediaPermissionRequest:
                request_allow("user_media")

    def on_download(self, session, download):
        download.connect("decide-destination", self.on_decide_dest)

    def on_decide_dest(self, download, filename):
        def on_save(dialog, result, error=None):
            if error:
                print(error)
                return
            file = dialog.save_finish(result)
            path = file.get_path()
            download.set_destination(path)

        save_dialog = Gtk.FileDialog.new()
        save_dialog.set_title(_("Save File"))
        save_dialog.set_initial_name(filename)
        save_dialog.save(self, None, on_save)
        return True

    def on_hide(self, button):
        self.set_visible(False)

    def on_fullscreen(self):
        self.toolbar.set_reveal_top_bars(not self.is_fullscreen())

    def toggle_fullscreen(self):
        self.unfullscreen() if self.is_fullscreen() else self.fullscreen()

    def close_fullscreen(self):
        if self.is_fullscreen():
            self.unfullscreen()
