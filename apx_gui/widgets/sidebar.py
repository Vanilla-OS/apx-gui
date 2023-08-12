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
import gettext as _

from apx_gui.widgets.entry_subsystem import EntrySubsystem
from apx_gui.widgets.entry_stack import EntryStack
from apx_gui.widgets.entry_pkgmanager import EntryPkgManager
from apx_gui.widgets.editor import Editor
from apx_gui.core.apx_entities import Subsystem, Stack, PkgManager


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/sidebar.ui")
class Sidebar(Gtk.Box):
    __gtype_name__: str = "Sidebar"
    __registry__: dict = {}

    list_subsystems: Gtk.ListBox = Gtk.Template.Child()
    list_stacks: Gtk.ListBox = Gtk.Template.Child()
    list_pkgmanagers: Gtk.ListBox = Gtk.Template.Child()
    stack_sidebar: Adw.ViewStack = Gtk.Template.Child()
    btn_show_subsystems: Gtk.Button = Gtk.Template.Child()
    btn_show_stacks: Gtk.Button = Gtk.Template.Child()
    btn_show_pkgmanagers: Gtk.Button = Gtk.Template.Child()

    def __init__(
        self,
        window: Adw.ApplicationWindow,
        subsystems: list[Subsystem],
        stacks: list[Stack],
        pkgmanagers: list[PkgManager],
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__subsystems: list[Subsystem] = subsystems
        self.__stacks: list[Stack] = stacks
        self.__pkgmanagers: list[PkgManager] = pkgmanagers
        self.__build_ui()

    def __build_ui(self) -> None:
        self.btn_show_subsystems.connect("clicked", self.__switch_stack, "subsystems")
        self.btn_show_stacks.connect("clicked", self.__switch_stack, "stacks")
        self.btn_show_pkgmanagers.connect("clicked", self.__switch_stack, "pkgmanagers")
        self.list_subsystems.connect("row-selected", self.__on_subsystem_selected)
        self.list_stacks.connect("row-selected", self.__on_stack_selected)
        self.list_pkgmanagers.connect("row-selected", self.__on_pkgmanager_selected)

        for subsystem in self.__subsystems:
            entry = EntrySubsystem(subsystem)
            self.list_subsystems.append(entry)
            self.__registry__[subsystem.aid] = entry

        for stack in self.__stacks:
            entry = EntryStack(stack)
            self.list_stacks.append(entry)
            self.__registry__[stack.aid] = entry

        for pkgmanager in self.__pkgmanagers:
            entry = EntryPkgManager(pkgmanager)
            self.list_pkgmanagers.append(entry)
            self.__registry__[pkgmanager.aid] = entry

    def __switch_stack(self, button: Gtk.Button, name: str) -> None:
        for btn in [
            self.btn_show_subsystems,
            self.btn_show_stacks,
            self.btn_show_pkgmanagers,
        ]:
            if btn != button:
                btn.add_css_class("flat")
        self.stack_sidebar.set_visible_child_name(name)

        button.remove_css_class("flat")

    def __on_subsystem_selected(
        self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow
    ) -> None:
        if row is None:
            return

        if self.__window.editor.is_open(row.subsystem.aid):
            self.__window.editor.open(row.subsystem.aid)
            return

        self.__window.editor.new_subsystem_tab(row.subsystem)

    def __on_stack_selected(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        if row is None:
            return

        if self.__window.editor.is_open(row.stack.aid):
            self.__window.editor.open(row.stack.aid)
            return

        self.__window.editor.new_stack_tab(row.stack)

    def __on_pkgmanager_selected(
        self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow
    ) -> None:
        if row is None:
            return

        if self.__window.editor.is_open(row.pkgmanager.aid):
            self.__window.editor.open(row.pkgmanager.aid)
            return

        self.__window.editor.new_pkgmanager_tab(row.pkgmanager)

    def remove_subsystem(self, aid: str) -> None:
        self.list_subsystems.remove(self.__registry__[aid])
        self.__registry__.pop(aid)

    def remove_stack(self, aid: str) -> None:
        self.list_stacks.remove(self.__registry__[aid])
        self.__registry__.pop(aid)

    def remove_pkgmanager(self, aid: str) -> None:
        self.list_pkgmanagers.remove(self.__registry__[aid])
        self.__registry__.pop(aid)

    def new_subsystem(self, subsystem: Subsystem) -> None:
        entry = EntrySubsystem(subsystem)
        self.list_subsystems.append(entry)
        self.__registry__[subsystem.aid] = entry

    def new_stack(self, stack: Stack) -> None:
        entry = EntryStack(stack)
        self.list_stacks.append(entry)
        self.__registry__[stack.aid] = entry

    def new_pkgmanager(self, pkgmanager: PkgManager) -> None:
        entry = EntryPkgManager(pkgmanager)
        self.list_pkgmanagers.append(entry)
        self.__registry__[pkgmanager.aid] = entry
