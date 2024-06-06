# tab_pkgmanager.py
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

from gi.repository import Gtk, Adw
from uuid import UUID

from gettext import gettext as _

from apx_gui.core.apx_entities import PkgManager
from apx_gui.core.run_async import RunAsync

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apx_gui.windows.main_window import ApxGUIWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/tab-pkgmanager.ui")
class TabPkgManager(Gtk.Box):
    __gtype_name__: str = "TabPkgManager"

    row_sudo: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_builtin: Adw.ActionRow = Gtk.Template.Child()  # pyright: ignore
    row_autoremove: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_install: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_clean: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_list: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_purge: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_remove: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_search: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_show: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_update: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_upgrade: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    btn_delete: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    sw_sudo: Gtk.Switch = Gtk.Template.Child()  # pyright: ignore
    infobar: Gtk.InfoBar = Gtk.Template.Child()  # pyright: ignore
    group_actions: Adw.PreferencesGroup = Gtk.Template.Child()  # pyright: ignore

    def __init__(
        self, window: Adw.ApplicationWindow, pkg_manager: PkgManager, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: ApxGUIWindow = window  # pyright: ignore
        self.__aid: UUID = pkg_manager.aid
        self.__pkgmanager: PkgManager = pkg_manager
        self.__build_ui()

    def __build_ui(self) -> None:
        self.sw_sudo.set_active(self.__pkgmanager.need_sudo)
        self.row_builtin.set_subtitle(
            _("Yes") if self.__pkgmanager.built_in else _("No")
        )
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

    @property
    def name(self) -> str:
        return self.__pkgmanager.name

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__window.toast(
                    _("{} package manager deleted").format(self.__pkgmanager.name)
                )
                self.__window.remove_pkgmanager(self.__aid)

        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            if response == "ok":
                self.__window.toast(
                    _("Deleting {} package manager...").format(self.__pkgmanager.name)
                )
                RunAsync(self.__pkgmanager.remove, on_callback, force=True)
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            _("Are you sure you want to delete the {} package manager?").format(
                self.__pkgmanager.name
            ),
            _(
                "This action will delete the package manager and all its data. This action cannot be undone."
            ),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("ok", _("Delete"))
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()

    def __update(self) -> bool:
        ok, _out = self.__pkgmanager.update(
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
        return ok

    def __on_sudo_changed(self, switch: Gtk.Switch, state: bool) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.need_sudo = state
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_autoremove_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_auto_remove = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_install_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_install = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_clean_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_clean = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_list_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_list = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_purge_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_purge = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_remove_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_remove = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_search_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_search = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_show_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_show = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_update_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_update = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)

    def __on_upgrade_apply(self, row: Adw.EntryRow) -> None:
        def on_callback(result: bool, *args) -> None:
            status: bool = result
            if status:
                self.__pkgmanager.cmd_upgrade = row.get_text()
                self.__window.toast(
                    _("{} package manager updated").format(self.__pkgmanager.name)
                )
            else:
                self.__window.toast(
                    _("Error updating {} package manager").format(
                        self.__pkgmanager.name
                    )
                )

        RunAsync(self.__update, on_callback)
