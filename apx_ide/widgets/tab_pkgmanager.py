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

from gi.repository import Gtk, Gio, GLib, GObject, Adw, GtkSource
from uuid import UUID
import json

from apx_ide.core.apx_entities import PkgManager


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/tab-pkgmanager.ui')
class TabPkgManager(Adw.PreferencesPage):
    __gtype_name__: str = 'TabPkgManager'
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

    def __init__(self, stack: PkgManager, **kwargs):
        super().__init__(**kwargs)
        self.__aid: UUID = stack.aid
        self.__pkgmanager: PkgManager = stack
        self.__build_ui()

    def __build_ui(self):
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

        self.btn_delete.connect('clicked', self.__on_btn_delete_clicked)

    @property
    def aid(self) -> UUID:
        return self.__aid

    def __on_btn_delete_clicked(self, button: Gtk.Button) -> None:
        print("Delete PkgManager")
