# main.py
#
# Copyright 2023 Mirko Brombin
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

import sys
import gi
import logging
from gettext import gettext as _
from typing import Text

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Gio, Adw
from apx_gui.windows.main_window import ApxGUIWindow


logging.basicConfig(level=logging.INFO)


class ApxGUIApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="org.vanillaos.ApxGUI",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

        self.__window: ApxGUIWindow = None

        self.create_action("quit", lambda *_: self.quit(), ["<primary>q"])
        self.create_action(
            "new_subsystem", self.on_new_subsystem_action, ["<primary>n"]
        )
        self.create_action("new_stack", self.on_new_stack_action, ["<primary>s"])
        self.create_action(
            "new_pkgmanager", self.on_new_pkgmanager_action, ["<primary>p"]
        )
        self.create_action("about", self.on_about_action)

    def do_activate(self) -> None:
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win: ApxGUIWindow = self.props.active_window
        if not win:
            win = ApxGUIWindow(application=self)

        self.__window = win
        win.present()

    def on_about_action(self, *args) -> None:
        """Callback for the app.about action."""
        about: Adw.AboutWindow = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Apx GUI",
            application_icon="org.vanillaos.ApxGUI",
            developer_name="Mirko Brombin",
            website="https://github.com/Vanilla-OS/apx-gui",
            issue_url="https://github.com/Vanilla-OS/apx-gui/issues",
            version="1.0.2",
            developers=["Mirko Brombin https://github.com/mirkobrombin"],
            translator_credits=_("translator_credits"),
            copyright="© 2023 Mirko Brombin and Contributors",
            license_type=("gpl-3-0-only"),
        )
        about.add_credit_section(
            _("Contributors"),
            [
                "K.B.Dharun Krishna https://github.com/kbdharun",
                "Mateus Melchiades https://github.com/matbme",
            ],
        )
        about.add_acknowledgement_section(
            _("Tools"),
            [
                "Apx https://github.com/Vanilla-OS/apx",
            ],
        )
        about.present()

    def on_new_subsystem_action(self, *args) -> None:
        self.__window.new_subsystem()

    def on_new_stack_action(self, *args) -> None:
        self.__window.new_stack()

    def on_new_pkgmanager_action(self, *args) -> None:
        self.__window.new_pkgmanager()

    def create_action(
        self, name: Text, callback: callable, shortcuts: list[str] = None
    ) -> None:
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def close(self, *args) -> None:
        """Close the application."""
        self.quit()


def main(version: Text) -> int:
    """The application's entry point."""
    app: ApxGUIApplication = ApxGUIApplication()
    return app.run(sys.argv)
