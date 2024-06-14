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

from gi.repository import Gtk, Gdk, GLib, Adw, Vte
from uuid import UUID

from gettext import gettext as _

from apx_gui.core.apx_entities import Subsystem
from apx_gui.core.run_async import RunAsync

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apx_gui.windows.main_window import ApxGUIWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/tab-subsystem.ui")
class TabSubsystem(Gtk.Box):
    __gtype_name__: str = "TabSubsystem"

    row_status: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_stack: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_pkgmanager: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_programs: Adw.ExpanderRow = Gtk.Template.Child()  # pyright: ignore
    row_startstop: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_reset: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_delete: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    btn_startstop: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_autoremove: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_clean: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_toggle_console: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_restart_console: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_reset: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_delete: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    box_console: Gtk.Box = Gtk.Template.Child()  # pyright: ignore

    console_initialized: bool = False
    gesture_controller: Gtk.GestureClick = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)

    def __init__(
        self, window: Adw.ApplicationWindow, subsystem: Subsystem, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: ApxGUIWindow = window  # pyright: ignore
        self.__aid: UUID = subsystem.aid
        self.__subsystem: Subsystem = subsystem

        self.btn_startstop.connect("clicked", self.__on_startstop_clicked)
        self.btn_autoremove.connect("clicked", self.__on_autoremove_clicked)
        self.btn_clean.connect("clicked", self.__on_clean_clicked)

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

        self.console: Vte.Terminal = self.__create_console()
        self.box_console.prepend(self.console)

        self.__rebuild_ui()

    def __rebuild_ui(self) -> None:
        self.row_status.set_subtitle(self.__subsystem.status)
        self.row_stack.set_subtitle(self.__subsystem.stack.name)
        self.row_pkgmanager.set_subtitle(self.__subsystem.stack.pkg_manager)
        self.row_programs.set_title(
            _("({}) Exported Programs").format(len(self.__subsystem.exported_programs))
        )

        if self.subsystem.running:
            self.row_startstop.set_title(_("Stop subsystem"))
            self.btn_startstop.set_icon_name("media-playback-stop-symbolic")
        else:
            self.row_startstop.set_title(_("Start subsystem"))
            self.btn_startstop.set_icon_name("media-playback-start-symbolic")

    def __create_console(self) -> Vte.Terminal:
        console: Vte.Terminal = Vte.Terminal()

        console.set_halign(Gtk.Align.FILL)
        console.set_valign(Gtk.Align.FILL)
        console.set_hexpand(True)
        console.set_vexpand(True)
        console.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        console.set_mouse_autohide(True)
        console.add_controller(self.gesture_controller)

        return console

    @property
    def aid(self) -> UUID:
        return self.__aid

    @property
    def subsystem(self) -> Subsystem:
        return self.__subsystem

    @property
    def name(self) -> str:
        return self.__subsystem.name

    def run_command(self, command: list[str]) -> None:
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
        def on_callback(result: tuple[bool, str], *args) -> None:
            status: bool = result[0]
            if status:
                self.__window.toast(_("{} subsystem reset").format(self.subsystem.name))

        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            if response == "ok":
                self.__window.toast(
                    _("Resetting {} subsystem...").format(self.subsystem.name)
                )
                RunAsync(self.__subsystem.reset, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            _("Are you sure you want to reset the {} subsystem?").format(
                self.subsystem.name
            ),
            _(
                "This action will reset the subsystem to its initial state. All the changes will be lost."
            ),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("ok", _("Reset"))
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: tuple[bool, str], *args) -> None:
            status: bool = result[0]
            if status:
                self.__window.toast(
                    _("{} subsystem deleted").format(self.subsystem.name)
                )
                self.__window.remove_subsystem(self.__aid, self.subsystem)

        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            if response == "ok":
                self.__window.toast(
                    _("Deleting {} subsystem...").format(self.subsystem.name)
                )
                RunAsync(self.__subsystem.remove, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            _("Are you sure you want to delete the {} subsystem?").format(
                self.subsystem.name
            ),
            _(
                "This action will delete the subsystem and all its data. This action cannot be undone."
            ),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("ok", _("Delete"))
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()

    def __on_startstop_clicked(self, button: Gtk.Button) -> None:
        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            if response == "ok":
                self.__window.toast(
                    _("Stopping {} subsystem...").format(self.subsystem.name)
                )
                self.subsystem.stop()
                dialog.destroy()

        if self.subsystem.running:
            dialog: Adw.MessageDialog = Adw.MessageDialog.new(
                self.__window,
                _("Are you sure you want to stop the {} subsystem?").format(
                    self.__subsystem.name
                ),
                _(
                    "This action will stop all running applications. Any unsaved progress will be lost."
                ),
            )
            dialog.add_response(_("cancel"), _("Cancel"))
            dialog.add_response(_("ok"), _("Stop"))
            dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.connect("response", on_response)
            dialog.present()
        else:
            self.__window.toast(
                _("Starting {} subsystem...").format(self.__subsystem.name)
            )
            self.subsystem.start()

    def __on_autoremove_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: tuple[bool, str], *args) -> None:
            ok, message = result
            if ok:
                self.__window.toast(_("Autoremove successful."))
            else:
                dialog: Adw.MessageDialog = Adw.MessageDialog.new(
                    self.__window,
                    _("Error encountered while running autoremove."),
                    message,
                )
                dialog.add_response(_("ok"), _("Ok"))
                dialog.connect("response", on_response)
                dialog.present()

        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            dialog.destroy()

        RunAsync(self.subsystem.autoremove, on_callback)
        self.__window.toast(_("Running autoremove..."))

    def __on_clean_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: tuple[bool, str], *args) -> None:
            ok, message = result
            if ok:
                self.__window.toast(_("Package cache clean successful."))
            else:
                dialog: Adw.MessageDialog = Adw.MessageDialog.new(
                    self.__window,
                    _("Error encountered while cleaning package cache."),
                    message,
                )
                dialog.add_response(_("ok"), _("Ok"))
                dialog.connect("response", on_response)
                dialog.present()

        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            dialog.destroy()

        RunAsync(self.subsystem.clean, on_callback)
        self.__window.toast(_("Running clean operation..."))

    def update_page(self, subsystem: Subsystem) -> None:
        self.__subsystem = subsystem

        if not subsystem.running:
            self.box_console.hide()
            self.btn_restart_console.hide()
            self.console_initialized = False
            self.console.reset(True, True)

        self.__rebuild_ui()
