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
from gi.repository import Gtk, GLib, Gdk, Adw

from apx_ide.core.run_async import RunAsync
from apx_ide.core.apx import Apx
from apx_ide.widgets.editor import Editor
from apx_ide.widgets.sidebar import Sidebar


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/window-main.ui')
class ApxIDEWindow(Adw.ApplicationWindow):
    __gtype_name__: str = 'ApxIDEWindow'

    toasts: Adw.ToastOverlay = Gtk.Template.Child()
    paned_main: Gtk.Paned = Gtk.Template.Child()

    def __init__(self, embedded: bool, **kwargs):
        super().__init__(**kwargs)

        self.__apx: Apx = Apx()
        self.__build_ui()

    def __build_ui(self):
        editor: Editor = Editor()
        self.paned_main.set_end_child(editor)

        sidebar: Sidebar = Sidebar(
            self.__apx.subsystems_list(), 
            self.__apx.stacks_list(), 
            self.__apx.pkgmanagers_list(),
            editor
        )
        self.paned_main.set_start_child(sidebar)
