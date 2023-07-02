# tab-subsystem.py
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

from apx_ide.core.apx_entities import Subsystem


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/tab-subsystem.ui')
class TabSubsystem(Adw.PreferencesPage):
    __gtype_name__ = 'TabSubsystem'
    row_status = Gtk.Template.Child()
    row_stack = Gtk.Template.Child()
    row_pkgmanager = Gtk.Template.Child()
    row_packages = Gtk.Template.Child()
    row_console = Gtk.Template.Child()
    row_reset = Gtk.Template.Child()
    row_delete = Gtk.Template.Child()

    def __init__(self, subsystem: Subsystem, **kwargs):
        super().__init__(**kwargs)
        self.__aid = subsystem.aid
        self.__subsystem = subsystem
        self.__build_ui()

    def __build_ui(self):
        self.row_status.set_subtitle(self.__subsystem.status)
        self.row_stack.set_subtitle(self.__subsystem.stack.name)
        self.row_pkgmanager.set_subtitle(self.__subsystem.stack.pkg_manager)
        self.row_packages.set_title(f"Packages ({len(self.__subsystem.stack.packages)})")

        for package in self.__subsystem.stack.packages:
            self.row_packages.add_row(Adw.ActionRow(title=package))

    @property
    def aid(self):
        return self.__aid

    @property
    def subsystem(self):
        return self.__subsystem
