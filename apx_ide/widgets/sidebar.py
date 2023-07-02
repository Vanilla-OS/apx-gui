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

from gi.repository import Gtk, Gio, GObject, Adw

from apx_ide.widgets.entry_subsystem import EntrySubsystem
from apx_ide.widgets.editor import Editor
from apx_ide.core.apx_entities import Subsystem


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/sidebar.ui')
class Sidebar(Gtk.Box):
    __gtype_name__ = 'Sidebar'

    list_subsystems = Gtk.Template.Child()
    stack_sidebar = Gtk.Template.Child()
    btn_show_subsystems = Gtk.Template.Child()
    btn_show_stacks = Gtk.Template.Child()
    btn_show_pkgmanagers = Gtk.Template.Child()

    def __init__(self, subsystems: list[Subsystem], editor: Editor, **kwargs):
        super().__init__(**kwargs)
        self.__subsystems = subsystems
        self.__editor = editor
        self.__build_ui()

    def __build_ui(self):
        self.btn_show_subsystems.connect('clicked', self.__switch_stack, 'subsystems')
        self.btn_show_stacks.connect('clicked', self.__switch_stack, 'stacks')
        self.btn_show_pkgmanagers.connect('clicked', self.__switch_stack, 'pkgmanagers')
        self.list_subsystems.connect('row-selected', self.__on_subsystem_selected)

        for subsystem in self.__subsystems:
            entry = EntrySubsystem(subsystem)
            self.list_subsystems.append(entry)
            
    def __switch_stack(self, button, name):
        for btn in [
            self.btn_show_subsystems, 
            self.btn_show_stacks, 
            self.btn_show_pkgmanagers
        ]:
            if btn != button:
                btn.add_css_class('flat')
        self.stack_sidebar.set_visible_child_name(name)

        button.remove_css_class('flat')

    def __on_subsystem_selected(self, listbox, row):
        if self.__editor.is_open(row.aid):
            self.__editor.open(row.aid)
            return

        self.__editor.new_subsystem_tab(row.subsystem)
