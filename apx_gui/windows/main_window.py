# main_window.py
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

import os
import subprocess
from gi.repository import Gtk, GLib, Gdk, Gio, Adw

from apx_gui.core.run_async import RunAsync
from apx_gui.core.apx import Apx
from apx_gui.core.apx_entities import Subsystem, Stack, PkgManager
from apx_gui.widgets.editor import Editor
from apx_gui.widgets.sidebar import Sidebar
from apx_gui.windows.create_subsystem import CreateSubsystemWindow
from apx_gui.windows.create_stack import CreateStackWindow
from apx_gui.windows.create_pkgmanager import CreatePkgManagerWindow


@Gtk.Template(resource_path='/org/vanillaos/apx-gui/gtk/window-main.ui')
class ApxGUIWindow(Adw.ApplicationWindow):
    __gtype_name__: str = 'ApxGUIWindow'

    toasts: Adw.ToastOverlay = Gtk.Template.Child()
    paned_main: Gtk.Paned = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.__apx: Apx = Apx()
        self.__subsystems: list[Subsystem] = self.__apx.subsystems_list()
        self.__stacks: list[Stack] = self.__apx.stacks_list()
        self.__pkgmanagers: list[PkgManager] = self.__apx.pkgmanagers_list()

        self.__build_ui()

    def __build_ui(self) -> None:
        self.editor: Editor = Editor(self)
        self.paned_main.set_end_child(self.editor)

        self.sidebar: Sidebar = Sidebar(
            self,
            self.__subsystems,
            self.__stacks,
            self.__pkgmanagers  
        )
        self.paned_main.set_start_child(self.sidebar)

    def toast(self, message: str, timeout: int=2) -> Adw.Toast:
        toast: Adw.Toast = Adw.Toast.new(message)
        toast.props.timeout = timeout
        self.toasts.add_toast(toast)
        return toast
    
    def append_subsystem(self, subsystem: Subsystem) -> None:
        self.__subsystems.append(subsystem)
        self.sidebar.new_subsystem(subsystem)

    def append_stack(self, stack: Stack) -> None:
        self.__stacks.append(stack)
        self.sidebar.new_stack(stack)

    def append_pkgmanager(self, pkgmanager: PkgManager) -> None:
        self.__pkgmanagers.append(pkgmanager)
        self.sidebar.new_pkgmanager(pkgmanager)

    def remove_subsystem(self, aid: str) -> None:
        self.editor.close(aid)
        self.sidebar.remove_subsystem(aid)

    def remove_stack(self, aid: str) -> None:
        self.editor.close(aid)
        self.sidebar.remove_stack(aid)

    def remove_pkgmanager(self, aid: str) -> None:
        self.editor.close(aid)
        self.sidebar.remove_pkgmanager(aid)

    def new_subsystem(self) -> None:
        window: CreateSubsystemWindow = CreateSubsystemWindow(
            self, 
            self.__subsystems,
            self.__stacks 
        )
        window.show()

    def new_stack(self) -> None:
        window: CreateStackWindow = CreateStackWindow(
            self, 
            self.__stacks,
            self.__pkgmanagers
        )
        window.show()

    def new_pkgmanager(self) -> None:
        window: CreatePkgManagerWindow = CreatePkgManagerWindow(
            self, 
            self.__pkgmanagers
        )
        window.show()
