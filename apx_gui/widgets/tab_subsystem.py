# tab_subsystem.py
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

from gi.repository import Gtk, Gdk, Gio, GLib, GObject, Adw, Vte, Pango
from uuid import UUID
from typing import List, Dict, Optional, Tuple, Text

from apx_gui.core.apx_entities import Subsystem
from apx_gui.core.run_async import RunAsync


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/tab-subsystem.ui")
class TabSubsystem(Gtk.Box):
    __gtype_name__: Text = "TabSubsystem"

    row_status: Adw.ActionRow = Gtk.Template.Child()
    row_stack: Adw.ActionRow = Gtk.Template.Child()
    row_pkgmanager: Adw.ActionRow = Gtk.Template.Child()
    row_programs: Adw.ExpanderRow = Gtk.Template.Child()
    row_reset: Adw.ActionRow = Gtk.Template.Child()
    row_delete: Adw.ActionRow = Gtk.Template.Child()
    btn_toggle_console: Gtk.Button = Gtk.Template.Child()
    btn_restart_console: Gtk.Button = Gtk.Template.Child()
    btn_reset: Gtk.Button = Gtk.Template.Child()
    btn_delete: Gtk.Button = Gtk.Template.Child()
    box_console: Gtk.Box = Gtk.Template.Child()

    console: Vte.Terminal = Vte.Terminal()
    console_initialized: bool = False
    gesture_controller: Gtk.GestureClick = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)

    def __init__(
        self, window: Adw.ApplicationWindow, subsystem: Subsystem, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__aid: UUID = subsystem.aid
        self.__subsystem: Subsystem = subsystem
        self.__build_ui()

    def __build_ui(self) -> None:
        self.row_status.set_subtitle(self.__subsystem.status)
        self.row_stack.set_subtitle(self.__subsystem.stack.name)
        self.row_pkgmanager.set_subtitle(self.__subsystem.stack.pkg_manager)
        self.row_programs.set_title(
            f"({len(self.__subsystem.exported_programs)}) Exported Programs"
        )

        self.btn_toggle_console.connect("clicked", self.__on_console_clicked)
        self.btn_restart_console.connect("clicked", self.__on_reset_console_clicked)
        self.btn_reset.connect("clicked", self.__on_reset_clicked)
        self.btn_delete.connect("clicked", self.__on_delete_clicked)

        for name, program in self.__subsystem.exported_programs.items():
            row: Adw.ActionRow = Adw.ActionRow(
                title=name, subtitle=program.get("GenericName", "")
            )
            row.set_icon_name(program.get("Icon", "application-x-executable-symbolic"))
            self.row_programs.add_row(row)

        console: Vte.Terminal = self.__create_console()
        self.box_console.prepend(self.console)

    def __create_console(self) -> Vte.Terminal:
        self.console.set_halign(Gtk.Align.FILL)
        self.console.set_valign(Gtk.Align.FILL)
        self.console.set_hexpand(True)
        self.console.set_vexpand(True)
        self.console.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        self.console.set_mouse_autohide(True)
        self.console.add_controller(self.gesture_controller)
        return self.console

    @property
    def aid(self) -> UUID:
        return self.__aid

    @property
    def subsystem(self) -> Subsystem:
        return self.__subsystem

    def run_command(self, command: List[str]) -> None:
        self.console.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            None,
            command,
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )

    def __on_console_clicked(self, button: Gtk.Button) -> None:
        if self.box_console.get_visible():
            self.box_console.hide()
            self.btn_restart_console.hide()
        else:
            self.box_console.show()
            self.btn_restart_console.show()

        if not self.console_initialized:
            self.run_command(self.__subsystem.enter_command)
            self.console_initialized = True

    def __on_reset_console_clicked(self, button: Gtk.Button) -> None:
        self.console.reset(True, True)
        self.run_command(self.__subsystem.enter_command)

    def __on_reset_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: Tuple[bool, str], *args) -> None:
            status: bool = result[0]
            if status:
                self.__window.toast(f"{self.__subsystem.name} subsystem reset")

        def on_response(dialog: Adw.MessageDialog, response: Text) -> None:
            if response == "ok":
                self.__window.toast(f"Resetting {self.__subsystem.name} subsystem...")
                RunAsync(self.__subsystem.reset, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            f"Are you sure you want to reset the {self.__subsystem.name} subsystem?",
            "This action will reset the subsystem to its initial state. All the changes will be lost.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("ok", "Reset")
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: Tuple[bool, str], *args) -> None:
            status: bool = result[0]
            if status:
                self.__window.toast(f"{self.__subsystem.name} subsystem deleted")
                self.__window.remove_subsystem(self.__aid)

        def on_response(dialog: Adw.MessageDialog, response: Text) -> None:
            if response == "ok":
                self.__window.toast(f"Deleting {self.__subsystem.name} subsystem...")
                RunAsync(self.__subsystem.remove, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            f"Are you sure you want to delete the {self.__subsystem.name} subsystem?",
            "This action will delete the subsystem and all its data. This action cannot be undone.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("ok", "Delete")
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()
