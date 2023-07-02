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

from gi.repository import Gtk, Gio, GLib, GObject, Adw
from uuid import UUID

from apx_ide.core.apx_entities import Subsystem


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/tab-subsystem.ui')
class TabSubsystem(Adw.PreferencesPage):
    __gtype_name__: str = 'TabSubsystem'

    row_status: Adw.ActionRow = Gtk.Template.Child()
    row_stack: Adw.ActionRow = Gtk.Template.Child()
    row_pkgmanager: Adw.ActionRow = Gtk.Template.Child()
    row_programs: Adw.ExpanderRow = Gtk.Template.Child()
    row_console: Adw.ActionRow = Gtk.Template.Child()
    row_reset: Adw.ActionRow = Gtk.Template.Child()
    row_delete: Adw.ActionRow = Gtk.Template.Child()
    btn_console: Gtk.Button = Gtk.Template.Child()
    btn_reset: Gtk.Button = Gtk.Template.Child()
    btn_delete: Gtk.Button = Gtk.Template.Child()

    def __init__(self, subsystem: Subsystem, **kwargs):
        super().__init__(**kwargs)
        self.__aid: UUID = subsystem.aid
        self.__subsystem: Subsystem = subsystem
        self.__build_ui()

    def __build_ui(self):
        self.row_status.set_subtitle(self.__subsystem.status)
        self.row_stack.set_subtitle(self.__subsystem.stack.name)
        self.row_pkgmanager.set_subtitle(self.__subsystem.stack.pkg_manager)
        self.row_programs.set_title(f"({len(self.__subsystem.exported_programs)}) Exported Programs")

        self.btn_console.connect('clicked', self.__on_console_clicked)
        self.btn_reset.connect('clicked', self.__on_reset_clicked)
        self.btn_delete.connect('clicked', self.__on_delete_clicked)

        for program in self.__subsystem.exported_programs:
            self.row_programs.add_row(Adw.ActionRow(title=program))

    @property
    def aid(self) -> UUID:
        return self.__aid

    @property
    def subsystem(self) -> Subsystem:
        return self.__subsystem

    def __on_console_clicked(self, button: Gtk.Button) -> None:
        GLib.spawn_command_line_async(f"kgx -e apx2 {self.__subsystem.name} enter")

    def __on_reset_clicked(self, button: Gtk.Button) -> None:
        print("Reset clicked")

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        print("Delete clicked")
