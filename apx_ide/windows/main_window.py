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

from apx_ide.utils.run_async import RunAsync
from apx_ide.widgets.tab_subsystem import TabSubsystem


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/window-main.ui')
class ApxIDEWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ApxIDEWindow'
    toasts = Gtk.Template.Child()
    tabs_editor = Gtk.Template.Child()
    stack_main = Gtk.Template.Child()
    btn_show_subsystems = Gtk.Template.Child()
    btn_show_stacks = Gtk.Template.Child()
    btn_show_pkgmanagers = Gtk.Template.Child()

    def __init__(self, embedded, **kwargs):
        super().__init__(**kwargs)

        page = self.tabs_editor.append(TabSubsystem())
        page.set_title('Subsystem')
        page = self.tabs_editor.append(TabSubsystem())
        page.set_title('Subsystem 2')

        self.stack_main.set_visible_child_name('subsystems')
        self.btn_show_subsystems.connect('clicked', self._switch_stack, 'subsystems')
        self.btn_show_stacks.connect('clicked', self._switch_stack, 'stacks')
        self.btn_show_pkgmanagers.connect('clicked', self._switch_stack, 'pkgmanagers')

    def _switch_stack(self, button, name):
        for btn in [
            self.btn_show_subsystems, 
            self.btn_show_stacks, 
            self.btn_show_pkgmanagers
        ]:
            if btn != button:
                btn.add_css_class('flat')
        self.stack_main.set_visible_child_name(name)

        button.remove_css_class('flat')

