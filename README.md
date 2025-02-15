# Web Apps

![Web Apps logo](data/icons/hicolor/96x96/apps/net.codelogistics.webapps.png)

### Install websites as desktop applications

Install websites as desktop apps, so that they appear in their own windows separate from any browsers installed. This is similar to the "Install as App" feature found in popular web browsers.

It uses an internal browser isolated from the system browser, which can optionally be used in incognito mode. Links to websites other than the one installed open in a new browser window.

[![Get it on Flathub](https://flathub.org/api/badge?locale=en)](https://flathub.org/apps/net.codelogistics.webapps/)

## Translations

Translations are managed with [Codeberg Weblate](https://translate.codeberg.org/engage/web-apps/).

[![Translation status](https://translate.codeberg.org/widget/web-apps/web-apps/287x66-black.png)](https://translate.codeberg.org/engage/web-apps/)

## Installation

Web Apps is available on Flathub [here](https://flathub.org/apps/net.codelogistics.webapps).

You can install it from GNOME Software, Discover or by using the following command:

`flatpak install flathub net.codelogistics.webapps`

This is application is made for Flatpak only.

## Common Issues

**Cannot create web apps on Ubuntu-based distros**

This is due to a bug in Ubuntu (see [#72](https://codeberg.org/eyekay/webapps/issues/72) for further details). A workaround for this issue is available [here](https://etbe.coker.com.au/2024/04/24/ubuntu-24-04-bubblewrap/).

**Does not work on KDE/ XFCE/ any DE other than GNOME**

Web Apps uses the Dynamic Launcher portal from xdg-desktop-portal to install the .desktop file for web apps. However, support for this portal varies depending on the xdg-desktop-portal backend used by your DE.

On KDE, a workaround is to make the desktop files at ~/.local/share/applications/net.codelogistics.webapps.\* and ~/.local/share/xdg-desktop-portal/applications/net.codelogistics.webapps.\* executable.

**CAPTCHA/ login page/ blank page opens in the default browser**

Web pages with a domain name other than the domain name of the URL of the web app will by default open in the system's default web browser. You can alter this behaviour by changing the value for "Domain Matching" in the web app's settings.

**No content visible with NVIDIA graphics card**

The workaround is to set the environment variable ``WEBKIT_DISABLE_DMABUF_RENDERER=1``. This can be done using Flatseal. [Reference](https://github.com/hugolabe/Wike/issues/172)

## Building

You can build Web Apps by cloning this repository into GNOME Builder (either the Flatpak or the version shipped with your distro), which will handle all dependencies and build the Flatpak.

## Code of Conduct

Web Apps uses the [GNOME Code of Conduct](https://conduct.gnome.org/).

## License

This program is licensed under the GNU General Public License, version 3.0 or later.

## Credits

Made with Gtk 4, WebKitGTK, libadwaita, XDG Desktop Portal and Flatpak.