# sidebar.py
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

from gi.repository import Gtk, Gio, GObject, Adw

from apx_ide.widgets.entry_subsystem import EntrySubsystem
from apx_ide.widgets.entry_stack import EntryStack
from apx_ide.widgets.entry_pkgmanager import EntryPkgManager
from apx_ide.widgets.editor import Editor
from apx_ide.core.apx_entities import Subsystem, Stack, PkgManager


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/sidebar.ui')
class Sidebar(Gtk.Box):
    __gtype_name__: str = 'Sidebar'

    list_subsystems: Gtk.ListBox = Gtk.Template.Child()
    list_stacks: Gtk.ListBox = Gtk.Template.Child()
    list_pkgmanagers: Gtk.ListBox = Gtk.Template.Child()
    stack_sidebar: Adw.ViewStack = Gtk.Template.Child()
    btn_show_subsystems: Gtk.Button = Gtk.Template.Child()
    btn_show_stacks: Gtk.Button = Gtk.Template.Child()
    btn_show_pkgmanagers: Gtk.Button = Gtk.Template.Child()

    def __init__(self, subsystems: list[Subsystem], stacks: list[Stack], pkgmanagers: list[PkgManager], editor: Editor, **kwargs):
        super().__init__(**kwargs)
        self.__subsystems: list[Subsystem] = subsystems
        self.__stacks: list[Stack] = stacks
        self.__pkgmanagers: list[PkgManager] = pkgmanagers
        self.__editor: Editor = editor
        self.__build_ui()

    def __build_ui(self):
        self.btn_show_subsystems.connect('clicked', self.__switch_stack, 'subsystems')
        self.btn_show_stacks.connect('clicked', self.__switch_stack, 'stacks')
        self.btn_show_pkgmanagers.connect('clicked', self.__switch_stack, 'pkgmanagers')
        self.list_subsystems.connect('row-selected', self.__on_subsystem_selected)
        self.list_stacks.connect('row-selected', self.__on_stack_selected)
        self.list_pkgmanagers.connect('row-selected', self.__on_pkgmanager_selected)

        for subsystem in self.__subsystems:
            entry = EntrySubsystem(subsystem)
            self.list_subsystems.append(entry)

        for stack in self.__stacks:
            entry = EntryStack(stack)
            self.list_stacks.append(entry)

        for pkgmanager in self.__pkgmanagers:
            entry = EntryPkgManager(pkgmanager)
            self.list_pkgmanagers.append(entry)

    def __switch_stack(self, button: Gtk.Button, name: str):
        for btn in [
            self.btn_show_subsystems, 
            self.btn_show_stacks, 
            self.btn_show_pkgmanagers
        ]:
            if btn != button:
                btn.add_css_class('flat')
        self.stack_sidebar.set_visible_child_name(name)

        button.remove_css_class('flat')

    def __on_subsystem_selected(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow):
        if self.__editor.is_open(row.subsystem.aid):
            self.__editor.open(row.subsystem.aid)
            return

        self.__editor.new_subsystem_tab(row.subsystem)

    def __on_stack_selected(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow):
        if self.__editor.is_open(row.stack.aid):
            self.__editor.open(row.stack.aid)
            return

        self.__editor.new_stack_tab(row.stack)

    def __on_pkgmanager_selected(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow):
        if self.__editor.is_open(row.pkgmanager.aid):
            self.__editor.open(row.pkgmanager.aid)
            return

        self.__editor.new_pkgmanager_tab(row.pkgmanager)
