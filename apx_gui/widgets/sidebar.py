# sidebar.py
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

from apx_gui.widgets.entry_subsystem import EntrySubsystem
from apx_gui.widgets.entry_stack import EntryStack
from apx_gui.widgets.entry_pkgmanager import EntryPkgManager
from apx_gui.core.apx_entities import Subsystem, Stack, PkgManager

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apx_gui.windows.main_window import ApxGUIWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/sidebar.ui")
class Sidebar(Adw.Bin):
    __gtype_name__: str = "Sidebar"
    __registry__: dict[str, EntrySubsystem | EntryStack | EntryPkgManager] = {}

    list_subsystems: Gtk.ListBox = Gtk.Template.Child()  # pyright: ignore
    list_stacks: Gtk.ListBox = Gtk.Template.Child()  # pyright: ignore
    list_pkgmanagers: Gtk.ListBox = Gtk.Template.Child()  # pyright: ignore
    stack_sidebar: Adw.ViewStack = Gtk.Template.Child()  # pyright: ignore
    btn_new: Adw.SplitButton = Gtk.Template.Child()  # pyright: ignore
    sidebar_switcher: Adw.ViewSwitcher = Gtk.Template.Child() # pyright: ignore

    def __init__(
        self,
        window: Adw.ApplicationWindow,
        subsystems: list[Subsystem],
        stacks: list[Stack],
        pkgmanagers: list[PkgManager],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.__window: ApxGUIWindow = window  # pyright: ignore
        self.__subsystems: list[Subsystem] = subsystems
        self.__stacks: list[Stack] = stacks
        self.__pkgmanagers: list[PkgManager] = pkgmanagers
        self.__build_ui()

    def __build_ui(self) -> None:
        self.list_subsystems.connect("row-selected", self.__on_subsystem_selected)
        self.list_stacks.connect("row-selected", self.__on_stack_selected)
        self.list_pkgmanagers.connect("row-selected", self.__on_pkgmanager_selected)

        self.btn_new.connect("clicked", self.__on_btn_menu_clicked)

        for subsystem in self.__subsystems:
            entry = EntrySubsystem(subsystem)
            self.list_subsystems.append(entry)
            self.__registry__[str(subsystem.aid)] = entry

        for stack in self.__stacks:
            entry = EntryStack(stack)
            self.list_stacks.append(entry)
            self.__registry__[str(stack.aid)] = entry

        for pkgmanager in self.__pkgmanagers:
            entry = EntryPkgManager(pkgmanager)
            self.list_pkgmanagers.append(entry)
            self.__registry__[str(pkgmanager.aid)] = entry

    def __on_btn_menu_clicked(self, *args):
        current_list = self.stack_sidebar.get_visible_child()
        if current_list == self.list_subsystems:
            self.__window.new_subsystem()
        elif current_list == self.list_stacks:
            self.__window.new_stack()
        elif current_list == self.list_pkgmanagers:
            self.__window.new_pkgmanager()

    def __on_subsystem_selected(
        self, listbox: Gtk.ListBox, row: EntrySubsystem
    ) -> None:
        if row is None:
            return

        if self.__window.editor.is_open(row.subsystem.aid):
            self.__window.editor.open(row.subsystem.aid)
            return

        self.__window.editor.new_subsystem_tab(row.subsystem)

    def __on_stack_selected(self, listbox: Gtk.ListBox, row: EntryStack) -> None:
        if row is None:
            return

        if self.__window.editor.is_open(row.stack.aid):
            self.__window.editor.open(row.stack.aid)
            return

        self.__window.editor.new_stack_tab(row.stack)

    def __on_pkgmanager_selected(
        self, listbox: Gtk.ListBox, row: EntryPkgManager
    ) -> None:
        if row is None:
            return

        if self.__window.editor.is_open(row.pkgmanager.aid):
            self.__window.editor.open(row.pkgmanager.aid)
            return

        self.__window.editor.new_pkgmanager_tab(row.pkgmanager)

    def remove_subsystem(self, aid: UUID) -> None:
        self.list_subsystems.remove(self.__registry__[str(aid)])
        self.__registry__.pop(str(aid))

    def remove_stack(self, aid: UUID) -> None:
        self.list_stacks.remove(self.__registry__[str(aid)])
        self.__registry__.pop(str(aid))

    def remove_pkgmanager(self, aid: UUID) -> None:
        self.list_pkgmanagers.remove(self.__registry__[str(aid)])
        self.__registry__.pop(str(aid))

    def new_subsystem(self, subsystem: Subsystem) -> None:
        entry = EntrySubsystem(subsystem)
        self.list_subsystems.append(entry)
        self.__registry__[str(subsystem.aid)] = entry

    def new_stack(self, stack: Stack) -> None:
        entry = EntryStack(stack)
        self.list_stacks.append(entry)
        self.__registry__[str(stack.aid)] = entry

    def new_pkgmanager(self, pkgmanager: PkgManager) -> None:
        entry = EntryPkgManager(pkgmanager)
        self.list_pkgmanagers.append(entry)
        self.__registry__[str(pkgmanager.aid)] = entry

    def update_subsystem(self, subsystem: Subsystem) -> None:
        new_entry = EntrySubsystem(subsystem)

        idx = 0
        while (row := self.list_subsystems.get_row_at_index(idx)) is not None:
            if row.aid == subsystem.aid:  # pyright: ignore
                self.remove_subsystem(subsystem.aid)
                self.list_subsystems.insert(new_entry, idx)
                break
            idx += 1

        self.__registry__[str(subsystem.aid)] = new_entry
