# create_pkgmanager.py
#
# Copyright 2024 Mirko Brombin
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
# SPDX-License-Identifier: GPL-3.0-only

from gi.repository import Gtk, Adw
from gettext import gettext as _

from apx_gui.core.apx_entities import PkgManager
from apx_gui.utils.gtk import GtkUtils
from apx_gui.core.run_async import RunAsync

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apx_gui.windows.main_window import ApxGUIWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/create-pkgmanager.ui")
class CreatePkgManagerWindow(Adw.Window):
    __gtype_name__ = "CreatePkgManagerWindow"

    __valid: set[str] = set([])

    btn_cancel: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_close: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_create: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    row_name: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_autoremove: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_clean: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_install: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_list: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_purge: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_remove: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_search: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_show: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_update: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_upgrade: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    stack_main: Adw.ViewStack = Gtk.Template.Child()  # pyright: ignore
    sw_sudo: Gtk.Switch = Gtk.Template.Child()  # pyright: ignore

    def __init__(
        self, window: Adw.ApplicationWindow, pkgmanagers: list[PkgManager], **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: ApxGUIWindow = window  # pyright: ignore
        self.__pkgmanagers: list[PkgManager] = pkgmanagers

        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_transient_for(self.__window)

        self.btn_cancel.connect("clicked", self.__on_cancel_clicked)
        self.btn_close.connect("clicked", self.__on_cancel_clicked)
        self.btn_create.connect("clicked", self.__on_create_clicked)
        self.row_name.connect("changed", self.__on_name_changed)
        self.row_autoremove.connect("changed", self.__on_command_changed)
        self.row_clean.connect("changed", self.__on_command_changed)
        self.row_install.connect("changed", self.__on_command_changed)
        self.row_list.connect("changed", self.__on_command_changed)
        self.row_purge.connect("changed", self.__on_command_changed)
        self.row_remove.connect("changed", self.__on_command_changed)
        self.row_search.connect("changed", self.__on_command_changed)
        self.row_show.connect("changed", self.__on_command_changed)
        self.row_update.connect("changed", self.__on_command_changed)
        self.row_upgrade.connect("changed", self.__on_command_changed)

    def __on_cancel_clicked(self, button: Gtk.Button) -> None:
        self.close()

    def __on_create_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: tuple[bool, PkgManager], *args):
            status: bool = result[0]
            pkgmanager: PkgManager = result[1]

            if status:
                self.__window.append_pkgmanager(pkgmanager)
                self.close()
                self.__window.toast(
                    _("Package manager {} created successfully").format(pkgmanager.name)
                )
                return

            self.stack_main.set_visible_child_name("error")

        def create_pkgmanager() -> tuple[bool, PkgManager]:
            pkgmanager: PkgManager = PkgManager(
                self.row_name.get_text(),
                self.sw_sudo.get_active(),
                self.row_autoremove.get_text(),
                self.row_clean.get_text(),
                self.row_install.get_text(),
                self.row_list.get_text(),
                self.row_purge.get_text(),
                self.row_remove.get_text(),
                self.row_search.get_text(),
                self.row_show.get_text(),
                self.row_update.get_text(),
                self.row_upgrade.get_text(),
                False,
            )
            return pkgmanager.create()

        button.set_visible(False)
        self.stack_main.set_visible_child_name("creating")
        RunAsync(create_pkgmanager, on_callback)

    def __on_name_changed(self, entry: Adw.EntryRow) -> None:
        name: str = entry.get_text()
        if name in [pkgmanager.name for pkgmanager in self.__pkgmanagers]:
            entry.add_css_class("error")
            self.btn_create.set_sensitive(False)
            return

        entry.remove_css_class("error")
        if GtkUtils.validate_entry(entry):
            self.__valid.add("name")
        else:
            self.__valid.remove("name")

        self.__check_validity()

    def __check_validity(self) -> None:
        self.btn_create.set_sensitive(len(list(self.__valid)) == 11)

    def __on_command_changed(self, entry: Adw.EntryRow) -> None:
        if GtkUtils.validate_entry(entry):
            self.__valid.add(entry.get_title())
        else:
            self.__valid.remove(entry.get_title())

        self.__check_validity()
