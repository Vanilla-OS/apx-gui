# tab_pkgmanager.py
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

from gi.repository import Gtk, Gio, GLib, GObject, Adw
from uuid import UUID
from typing import List, Optional, Text

from apx_gui.core.apx_entities import PkgManager
from apx_gui.core.run_async import RunAsync


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/tab-pkgmanager.ui")
class TabPkgManager(Gtk.Box):
    __gtype_name__: Text = "TabPkgManager"
    row_sudo: Adw.ActionRow = Gtk.Template.Child()
    row_builtin: Adw.ActionRow = Gtk.Template.Child()
    row_autoremove: Adw.EntryRow = Gtk.Template.Child()
    row_install: Adw.EntryRow = Gtk.Template.Child()
    row_clean: Adw.EntryRow = Gtk.Template.Child()
    row_list: Adw.EntryRow = Gtk.Template.Child()
    row_purge: Adw.EntryRow = Gtk.Template.Child()
    row_remove: Adw.EntryRow = Gtk.Template.Child()
    row_search: Adw.EntryRow = Gtk.Template.Child()
    row_show: Adw.EntryRow = Gtk.Template.Child()
    row_update: Adw.EntryRow = Gtk.Template.Child()
    row_upgrade: Adw.EntryRow = Gtk.Template.Child()
    btn_delete: Gtk.Button = Gtk.Template.Child()
    sw_sudo: Gtk.Switch = Gtk.Template.Child()
    infobar: Gtk.InfoBar = Gtk.Template.Child()
    group_actions: Adw.PreferencesGroup = Gtk.Template.Child()

    def __init__(
        self, window: Adw.ApplicationWindow, pkg_manager: PkgManager, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__aid: UUID = pkg_manager.aid
        self.__pkgmanager: PkgManager = pkg_manager
        self.__build_ui()

    def __build_ui(self) -> None:
        self.sw_sudo.set_active(self.__pkgmanager.need_sudo)
        self.row_builtin.set_subtitle("Yes" if self.__pkgmanager.built_in else "No")
        self.row_autoremove.set_text(self.__pkgmanager.cmd_auto_remove)
        self.row_install.set_text(self.__pkgmanager.cmd_install)
        self.row_clean.set_text(self.__pkgmanager.cmd_clean)
        self.row_list.set_text(self.__pkgmanager.cmd_list)
        self.row_purge.set_text(self.__pkgmanager.cmd_purge)
        self.row_remove.set_text(self.__pkgmanager.cmd_remove)
        self.row_search.set_text(self.__pkgmanager.cmd_search)
        self.row_show.set_text(self.__pkgmanager.cmd_show)
        self.row_update.set_text(self.__pkgmanager.cmd_update)
        self.row_upgrade.set_text(self.__pkgmanager.cmd_upgrade)

        if self.__pkgmanager.built_in:
            self.infobar.set_revealed(True)
            self.group_actions.set_visible(False)

            for row in [
                self.row_autoremove,
                self.row_install,
                self.row_clean,
                self.row_list,
                self.row_purge,
                self.row_remove,
                self.row_search,
                self.row_show,
                self.row_update,
                self.row_upgrade,
                self.row_sudo,
            ]:
                row.set_sensitive(False)

        self.btn_delete.connect("clicked", self.__on_delete_clicked)
        self.sw_sudo.connect("activate", self.__on_sudo_changed)
        self.row_autoremove.connect("apply", self.__on_autoremove_apply)
        self.row_install.connect("apply", self.__on_install_apply)
        self.row_clean.connect("apply", self.__on_clean_apply)
        self.row_list.connect("apply", self.__on_list_apply)
        self.row_purge.connect("apply", self.__on_purge_apply)
        self.row_remove.connect("apply", self.__on_remove_apply)
        self.row_search.connect("apply", self.__on_search_apply)
        self.row_show.connect("apply", self.__on_show_apply)
        self.row_update.connect("apply", self.__on_update_apply)
        self.row_upgrade.connect("apply", self.__on_upgrade_apply)

    @property
    def aid(self) -> UUID:
        return self.__aid

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__window.toast(f"{self.__pkgmanager.name} package manager deleted")
                self.__window.remove_pkgmanager(self.__aid)

        def on_response(dialog: Adw.MessageDialog, response: Text) -> None:
            if response == "ok":
                self.__window.toast(
                    f"Deleting {self.__pkgmanager.name} package manager..."
                )
                RunAsync(self.__pkgmanager.remove, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            f"Are you sure you want to delete the {self.__pkgmanager.name} package manager?",
            "This action will delete the package manager and all its data. This action cannot be undone.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("ok", "Delete")
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()

    def __update(self) -> bool:
        return self.__pkgmanager.update(
            self.sw_sudo.get_active(),
            self.row_autoremove.get_text(),
            self.row_install.get_text(),
            self.row_clean.get_text(),
            self.row_list.get_text(),
            self.row_purge.get_text(),
            self.row_remove.get_text(),
            self.row_search.get_text(),
            self.row_show.get_text(),
            self.row_update.get_text(),
            self.row_upgrade.get_text(),
        )

    def __on_sudo_changed(self, switch: Gtk.Switch, state: bool) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.need_sudo = state
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_autoremove_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_auto_remove = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_install_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_install = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_clean_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_clean = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_list_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_list = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_purge_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_purge = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_remove_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_remove = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_search_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_search = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_show_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_show = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_update_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_update = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)

    def __on_upgrade_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_upgrade = row.get_text()
                self.__window.toast(f"{self.__pkgmanager.name} package manager updated")
            else:
                self.__window.toast(
                    f"Error updating {self.__pkgmanager.name} package manager"
                )

        RunAsync(self.__update, on_callback)
