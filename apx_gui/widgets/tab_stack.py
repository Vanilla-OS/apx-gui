# tab_stack.py
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

from gi.repository import Gtk, Gio, GLib, GObject, Adw
from uuid import UUID
from typing import List, Text

from apx_gui.core.apx_entities import Stack
from apx_gui.core.run_async import RunAsync
from apx_gui.utils.gtk import GtkUtils


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/tab-stack.ui")
class TabStack(Gtk.Box):
    __gtype_name__: Text = "TabStack"

    row_base: Adw.EntryRow = Gtk.Template.Child()
    row_pkgmanager: Adw.EntryRow = Gtk.Template.Child()
    row_packages: Adw.ExpanderRow = Gtk.Template.Child()
    row_builtin: Adw.ActionRow = Gtk.Template.Child()
    btn_delete: Adw.ActionRow = Gtk.Template.Child()
    infobar: Gtk.InfoBar = Gtk.Template.Child()
    group_actions: Adw.PreferencesGroup = Gtk.Template.Child()

    def __init__(self, window: Adw.ApplicationWindow, stack: Stack, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__aid: UUID = stack.aid
        self.__stack: Stack = stack
        self.__build_ui()

    def __build_ui(self) -> None:
        self.row_base.set_text(self.__stack.base)
        self.row_pkgmanager.set_text(self.__stack.pkg_manager)
        self.row_packages.set_title(f"{len(self.__stack.packages)} Packages")
        self.row_builtin.set_subtitle("Yes" if self.__stack.built_in else "No")

        if self.__stack.built_in:
            self.infobar.set_revealed(True)
            self.group_actions.set_visible(False)
            for row in [
                self.row_base,
                self.row_pkgmanager,
            ]:
                row.set_sensitive(False)

        self.btn_delete.connect("clicked", self.__on_delete_clicked)
        self.row_base.connect("changed", self.__on_entry_changed)
        self.row_pkgmanager.connect("changed", self.__on_entry_changed)
        self.row_base.connect("apply", self.__on_base_apply)
        self.row_pkgmanager.connect("apply", self.__on_pkgmanager_apply)

        for pkg in self.__stack.packages:
            row: Adw.ActionRow = Adw.ActionRow()
            row.set_title(pkg)
            self.row_packages.add_row(row)
            if self.__stack.built_in:
                row.set_sensitive(False)

    @property
    def aid(self) -> UUID:
        return self.__aid

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__window.toast(f"{self.__stack.name} stack deleted")
                self.__window.remove_stack(self.__aid)

        def on_response(dialog: Adw.MessageDialog, response: Text) -> None:
            if response == "ok":
                self.__window.toast(f"Deleting {self.__stack.name} stack...")
                RunAsync(self.__stack.remove, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            f"Are you sure you want to delete the {self.__stack.name} stack?",
            "This action will delete the stack and all its data. This action cannot be undone.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("ok", "Delete")
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()

    def __on_entry_changed(self, row: Adw.EntryRow) -> None:
        GtkUtils.validate_entry(row)

    def __on_base_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__stack.base = row.get_text()
                self.__window.toast(f"{self.__stack.name} stack updated")
            else:
                self.__window.toast(f"Error updating {self.__stack.name} stack")

        RunAsync(self.__update, on_callback, base=row.get_text())

    def __on_pkgmanager_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__stack.pkg_manager = row.get_text()
                self.__window.toast(f"{self.__stack.name} stack updated")
            else:
                self.__window.toast(f"Error updating {self.__stack.name} stack")

        RunAsync(self.__update, on_callback, pkg_manager=row.get_text())

    def __update(
        self, base: Text = None, packages: List[str] = None, pkg_manager: Text = None
    ) -> bool:
        if base is None:
            base = self.__stack.base
        if packages is None:
            packages = self.__stack.packages
        if pkg_manager is None:
            pkg_manager = self.__stack.pkg_manager

        return self.__stack.update(base, packages, pkg_manager)
