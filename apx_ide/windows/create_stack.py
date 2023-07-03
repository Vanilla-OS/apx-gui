# create_stack.py
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

from apx_ide.core.apx_entities import PkgManager, Stack
from apx_ide.utils.gtk import GtkUtils
from apx_ide.core.run_async import RunAsync


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/create-stack.ui')
class CreateStackWindow(Adw.Window):
    __gtype_name__ = 'CreateStackWindow'
    __registry__: list[str] = []

    __valid_name: bool = False
    __valid_base: bool = False

    btn_cancel: Gtk.Button = Gtk.Template.Child()
    btn_create: Gtk.Button = Gtk.Template.Child()
    btn_add_package: Gtk.Button = Gtk.Template.Child()
    row_name: Adw.EntryRow = Gtk.Template.Child()
    row_base: Adw.EntryRow = Gtk.Template.Child()
    row_package: Adw.EntryRow = Gtk.Template.Child()
    row_pkgmanager: Adw.ComboRow = Gtk.Template.Child()
    str_pkgmanager: Gtk.StringList = Gtk.Template.Child() 
    group_packages: Adw.PreferencesGroup = Gtk.Template.Child()
    stack_main: Adw.ViewStack = Gtk.Template.Child()

    def __init__(
        self, 
        window: Adw.ApplicationWindow, 
        stacks: list[Stack], 
        pkgmanagers: list[PkgManager], 
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__stacks: list[Stack] = stacks
        self.__pkgmanagers: list[PkgManager] = pkgmanagers
        
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_transient_for(self.__window)

        for pkgmanager in self.__pkgmanagers:
            self.str_pkgmanager.append(pkgmanager.name)
        self.row_pkgmanager.set_selected(0)

        self.btn_cancel.connect('clicked', self.__on_cancel_clicked)
        self.btn_create.connect('clicked', self.__on_create_clicked)
        self.btn_add_package.connect('clicked', self.__on_add_package_clicked)
        self.row_name.connect('changed', self.__on_name_changed)
        self.row_base.connect('changed', self.__on_base_changed)
        self.row_package.connect('changed', self.__on_package_changed)

    def __on_cancel_clicked(self, button: Gtk.Button) -> None:
        self.close()

    def __on_create_clicked(self, button: Gtk.Button) -> None:
        def on_callback(result: [bool, Stack], *args):
            status: bool = result[0]
            stack: Stack = result[1]
            
            if status:
                self.__window.append_stack(stack)
                self.close()
                self.__window.toast(f"Stack {stack.name} created successfully")
                return

            self.stack_main.set_visible_child_name("error")
        
        def create_stack() -> [bool, Stack]:
            stack: Stack = Stack(
                self.row_name.get_text(),
                self.row_base.get_text(),
                self.__get_packages(),
                self.__pkgmanagers[self.row_pkgmanager.get_selected()].name,
                False
            )
            return stack.create()

        button.set_visible(False)
        self.stack_main.set_visible_child_name("creating")
        RunAsync(create_stack, on_callback)

    def __on_name_changed(self, entry: Adw.EntryRow) -> None:
        name: str = entry.get_text()
        if name in [stack.name for stack in self.__stacks]:
            entry.add_css_class("error")
            self.btn_create.set_sensitive(False)
            return

        entry.remove_css_class("error")
        self.__valid_name = GtkUtils.validate_entry(entry)
        self.__check_validity()

    def __on_base_changed(self, entry: Adw.EntryRow) -> None:
        self.__valid_base = GtkUtils.validate_entry(entry)
        self.__check_validity()

    def __check_validity(self) -> None:
        self.btn_create.set_sensitive(self.__valid_name and self.__valid_base)

    def __on_package_changed(self, entry: Adw.EntryRow) -> None:
        self.btn_add_package.set_sensitive(GtkUtils.validate_entry(entry))

    def __on_add_package_clicked(self, button: Gtk.Button) -> None:
        row: AdwActionRow = Adw.ActionRow(
            title=self.row_package.get_text(),
        )
        btn_remove: Gtk.Button = Gtk.Button.new_from_icon_name("edit-delete-symbolic")
        btn_remove.set_valign(Gtk.Align.CENTER)
        btn_remove.connect('clicked', self.__on_remove_package_clicked, row)
        row.add_suffix(btn_remove)

        self.group_packages.add(row)

        self.__registry__.append(self.row_package.get_text())
        self.row_package.set_text("")
        self.btn_add_package.set_sensitive(False)
        
    def __on_remove_package_clicked(self, button: Gtk.Button, row: Adw.ActionRow) -> None:
        self.group_packages.remove(row)
        self.__registry__.remove(row.get_title())
    
    def __get_packages(self) -> list[str]:
        return " ".join(self.__registry__)