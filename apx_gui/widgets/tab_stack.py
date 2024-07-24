# tab_stack.py
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
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk, Adw
from uuid import UUID

from gettext import gettext as _

from apx_gui.core.apx_entities import Stack
from apx_gui.core.run_async import RunAsync
from apx_gui.utils.gtk import GtkUtils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apx_gui.windows.main_window import ApxGUIWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/tab-stack.ui")
class TabStack(Gtk.Box):
    __gtype_name__: str = "TabStack"

    row_base: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_pkgmanager: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_packages: Adw.ExpanderRow = Gtk.Template.Child()  # pyright: ignore
    row_builtin: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    btn_delete: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    infobar: Gtk.InfoBar = Gtk.Template.Child()  # pyright: ignore
    group_actions: Adw.PreferencesGroup = Gtk.Template.Child()  # pyright: ignore

    def __init__(self, window: Adw.ApplicationWindow, stack: Stack, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__window: ApxGUIWindow = window  # pyright: ignore
        self.__aid: UUID = stack.aid
        self.__stack: Stack = stack
        self.__build_ui()

    def __build_ui(self) -> None:
        self.row_base.set_text(self.__stack.base)
        self.row_pkgmanager.set_text(self.__stack.pkg_manager)
        self.row_packages.set_title(_("{} Packages").format(len(self.__stack.packages)))
        self.row_builtin.set_subtitle(_("Yes") if self.__stack.built_in else _("No"))

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
            arow: Adw.ActionRow = Adw.ActionRow()
            arow.set_title(pkg)
            self.row_packages.add_row(arow)
            if self.__stack.built_in:
                arow.set_sensitive(False)

    @property
    def aid(self) -> UUID:
        return self.__aid

    @property
    def name(self) -> str:
        return self.__stack.name

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__window.toast(_("{} stack deleted").format(self.__stack.name))
                self.__window.remove_stack(self.__aid, self.__stack)

        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            if response == "ok":
                self.__window.toast(_("Deleting {} stack...").format(self.__stack.name))
                RunAsync(self.__stack.remove, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            _("Are you sure you want to delete the {} stack?").format(
                self.__stack.name
            ),
            _(
                "This action will delete the stack and all its data. This action cannot be undone."
            ),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("ok", _("Delete"))
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
                self.__window.toast(_("{} stack updated").format(self.__stack.name))
            else:
                self.__window.toast(
                    _("Error updating {} stack").format(self.__stack.name)
                )

        RunAsync(self.__update, on_callback, base=row.get_text())

    def __on_pkgmanager_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__stack.pkg_manager = row.get_text()
                self.__window.toast(_("{} stack updated").format(self.__stack.name))
            else:
                self.__window.toast(
                    _("Error updating {} stack").format(self.__stack.name)
                )

        RunAsync(self.__update, on_callback, pkg_manager=row.get_text())

    def __update(
        self,
        base: str | None = None,
        packages: list[str] | None = None,
        pkg_manager: str | None = None,
    ) -> bool:
        if base is None:
            base = self.__stack.base

        if packages is None:
            if type(self.__stack.packages) == list:
                packages_str = " ".join(self.__stack.packages)
            else:
                packages_str = str(self.__stack.packages)
        else:
            packages_str = " ".join(packages)

        if pkg_manager is None:
            pkg_manager = self.__stack.pkg_manager

        ok, _out = self.__stack.update(base, packages_str, pkg_manager)
        return ok
