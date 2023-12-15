# tab-editor.py
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

from gi.repository import Gtk, Adw, Gio
from typing import Dict, List, Optional, Union, Text
from uuid import UUID
from apx_gui.core.apx_entities import Subsystem, Stack, PkgManager
from apx_gui.widgets.tab_subsystem import TabSubsystem
from apx_gui.widgets.tab_stack import TabStack
from apx_gui.widgets.tab_pkgmanager import TabPkgManager


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/editor.ui")
class Editor(Adw.Bin):
    __gtype_name__: Text = "Editor"
    __registry__: Dict[str, Union[List[UUID], Dict[UUID, Adw.TabPage]]] = {
        "open": [],
        "tabs": {},
    }

    tabs_editor: Adw.TabView = Gtk.Template.Child()
    stack_editor: Adw.ViewStack = Gtk.Template.Child()
    page_no_tabs: Adw.ViewStackPage = Gtk.Template.Child()
    page_editor: Adw.ViewStackPage = Gtk.Template.Child()

    def __init__(self, window: Adw.ApplicationWindow, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__build_ui()

    def __build_ui(self) -> None:
        self.tabs_editor.connect("page-detached", self.__on_page_detached)
        self.tabs_editor.connect("page-attached", self.__on_page_attached)

    def __on_page_detached(self, tabs: Adw.TabView, page: Adw.TabPage, *args) -> None:
        self.__registry__["open"].remove(page.get_child().aid)
        self.__registry__["tabs"].pop(page.get_child().aid)

        if tabs.get_n_pages() == 0:
            self.stack_editor.set_visible_child_name("no_tabs")

    def __on_page_attached(self, tabs: Adw.TabView, page: Adw.TabPage, *args) -> None:
        self.page_no_tabs.set_visible(False)
        self.page_editor.set_visible(True)
        self.__registry__["open"].append(page.get_child().aid)
        self.__registry__["tabs"][page.get_child().aid] = page

        if tabs.get_n_pages() > 0:
            self.stack_editor.set_visible_child_name("editor")

    def open(self, aid: UUID) -> bool:
        if aid in self.__registry__["open"]:
            self.tabs_editor.set_selected_page(self.__registry__["tabs"][aid])
            return True
        return False

    def is_open(self, aid: UUID) -> bool:
        return aid in self.__registry__["open"]

    def new_subsystem_tab(self, subsystem: Subsystem) -> None:
        page: Adw.TabPage = self.tabs_editor.append(
            TabSubsystem(self.__window, subsystem)
        )
        icon: Gio.Icon = Gio.ThemedIcon.new_with_default_fallbacks(
            "utilities-terminal-symbolic"
        )

        page.set_title(subsystem.name)
        page.set_icon(icon)

        self.open(subsystem.aid)

    def new_stack_tab(self, stack: Stack) -> None:
        page: Adw.TabPage = self.tabs_editor.append(TabStack(self.__window, stack))
        icon: Gio.Icon = Gio.ThemedIcon.new_with_default_fallbacks(
            "vanilla-puzzle-piece-symbolic"
        )

        page.set_title(stack.name)
        page.set_icon(icon)

        self.open(stack.aid)

    def new_pkgmanager_tab(self, pkgmanager: PkgManager) -> None:
        page: Adw.TabPage = self.tabs_editor.append(
            TabPkgManager(self.__window, pkgmanager)
        )
        icon: Gio.Icon = Gio.ThemedIcon.new_with_default_fallbacks(
            "insert-object-symbolic"
        )

        page.set_title(pkgmanager.name)
        page.set_icon(icon)

        self.open(pkgmanager.aid)

    def close(self, aid: UUID) -> None:
        if self.is_open(aid):
            self.tabs_editor.close_page(self.__registry__["tabs"][aid])
