# create_subsystem.py
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
# SPDX-License-Identifier: GPL-3.0-only

from gi.repository import Gtk, GObject, Gio, Gdk, GLib, Adw, Vte, Pango

from apx_ide.core.apx_entities import Subsystem, Stack
from apx_ide.utils.gtk import GtkUtils
from apx_ide.core.run_async import RunAsync


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/create-subsystem.ui')
class CreateSubsystemWindow(Adw.Window):
    __gtype_name__ = 'CreateSubsystemWindow'

    btn_cancel: Gtk.Button = Gtk.Template.Child()
    btn_create: Gtk.Button = Gtk.Template.Child()
    row_name: Adw.EntryRow = Gtk.Template.Child()
    row_stack: Adw.ComboRow = Gtk.Template.Child()
    str_stack: Gtk.StringList = Gtk.Template.Child() 
    stack_main: Adw.ViewStack = Gtk.Template.Child()

    def __init__(
        self, 
        window: Adw.ApplicationWindow, 
        subsystems: list[Subsystem], 
        stacks: list[Stack], 
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__subsystems: list[Subsystem] = subsystems
        self.__stacks: list[Stack] = stacks
        
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_transient_for(self.__window)

        for stack in self.__stacks:
            self.str_stack.append(stack.name)
        self.row_stack.set_selected(0)

        self.btn_cancel.connect('clicked', self.__on_cancel_clicked)
        self.btn_create.connect('clicked', self.__on_create_clicked)
        self.row_name.connect('changed', self.__on_name_changed)

    def __on_cancel_clicked(self, button: Gtk.Button) -> None:
        self.close()

    def __on_create_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: [bool, Subsystem], *args):
            status: bool = result[0]
            subsystem: Subsystem = result[1]
            
            if status:
                self.__window.append_subsystem(subsystem)
                self.close()
                self.__window.toast(f"Subsystem {subsystem.name} created successfully")
                return

            self.stack_main.set_visible_child_name("error")
        
        def create_subsystem() -> [bool, Subsystem]:
            subsystem: Subsystem = Subsystem(
                None,
                self.row_name.get_text(),
                self.__stacks[self.row_stack.get_selected()],
                None
            )
            return subsystem.create()

        button.set_visible(False)
        self.stack_main.set_visible_child_name("creating")
        RunAsync(create_subsystem, on_callback)

    def __on_name_changed(self, entry: Adw.EntryRow) -> None:
        name: str = entry.get_text()
        if name in [subsystem.name for subsystem in self.__subsystems]:
            entry.add_css_class("error")
            self.btn_create.set_sensitive(False)
            return

        entry.remove_css_class("error")
        self.btn_create.set_sensitive(GtkUtils.validate_entry(entry))
