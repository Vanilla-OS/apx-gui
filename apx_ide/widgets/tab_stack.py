# tab_stack.py
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

from gi.repository import Gtk, Gio, GLib, GObject, Adw, GtkSource
from uuid import UUID
import json

from apx_ide.core.apx_entities import Stack


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/tab-stack.ui')
class TabStack(Gtk.Box):
    __gtype_name__: str = 'TabStack'
    row_base: Adw.EntryRow = Gtk.Template.Child()
    row_pkgmanager: Adw.EntryRow = Gtk.Template.Child()
    row_packages: Adw.ExpanderRow = Gtk.Template.Child()
    row_builtin: Adw.ActionRow = Gtk.Template.Child()
    btn_delete: Adw.ActionRow = Gtk.Template.Child()
    infobar: Gtk.InfoBar = Gtk.Template.Child()
    group_actions: Adw.PreferencesGroup = Gtk.Template.Child()

    def __init__(self, window: Adw.ApplicationWindow, stack: Stack, **kwargs):
        super().__init__(**kwargs)
        self.__window: Adw.ApplicationWindow = window
        self.__aid: UUID = stack.aid
        self.__stack: Stack = stack
        self.__build_ui()

    def __build_ui(self):
        # scrolled: Gtk.ScrolledWindow = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        # source_view: GtkSource.View = GtkSource.View(
        #     buffer=GtkSource.Buffer(
        #         highlight_syntax=True,
        #         highlight_matching_brackets=True,
        #         language=GtkSource.LanguageManager.get_default().get_language("json")
        #     ),
        #     show_line_numbers=True,
        #     show_line_marks=True,
        #     tab_width=4,
        #     monospace=True
        # )
        # print(self.__stack.to_json())
        # source_buffer: GtkSource.Buffer = source_view.get_buffer()
        # source_buffer.set_text(self.__stack.to_json(), -1)

        # scrolled.set_child(source_view)
        # self.set_start_child(scrolled)
        self.row_base.set_text(self.__stack.base)
        self.row_pkgmanager.set_text(self.__stack.pkg_manager)
        self.row_packages.set_title(f"{len(self.__stack.packages)} Packages")
        self.row_builtin.set_subtitle("Yes" if self.__stack.built_in else "No")

        if self.__stack.built_in:
            self.infobar.set_revealed(True)
            self.group_actions.set_visible(False)
            for row in [
                self.row_base,
                self.row_pkgmanager,
            ]:
                row.set_sensitive(False)

        self.btn_delete.connect('clicked', self.__on_delete_clicked)

        for pkg in self.__stack.packages:
            row: Adw.ActionRow = Adw.ActionRow()
            row.set_title(pkg)
            self.row_packages.add_row(row)
            if self.__stack.built_in:
                row.set_sensitive(False)

    @property
    def aid(self) -> UUID:
        return self.__aid

    def __on_delete_clicked(self, button: Gtk.Button) -> None:
        def on_response(dialog: Adw.MessageDialog, response: str) -> None:
            if response == "ok":
                print("Delete clicked")
            dialog.destroy()

        dialog: Adw.MessageDialog = Adw.MessageDialog.new(
            self.__window,
            f"Are you sure you want to delete the {self.__stack.name} stack?",
            "This action will delete the stack and all its data. This action cannot be undone.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("ok", "Delete")
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", on_response)
        dialog.present()
