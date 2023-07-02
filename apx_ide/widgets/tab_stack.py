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
class TabStack(Gtk.Paned):
    __gtype_name__: str = 'TabStack'

    def __init__(self, stack: Stack, **kwargs):
        super().__init__(**kwargs)
        self.__aid: UUID = stack.aid
        self.__stack: Stack = stack
        self.__build_ui()

    def __build_ui(self):
        scrolled: Gtk.ScrolledWindow = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        source_view: GtkSource.View = GtkSource.View(
            buffer=GtkSource.Buffer(
                highlight_syntax=True,
                highlight_matching_brackets=True,
                language=GtkSource.LanguageManager.get_default().get_language("json")
            ),
            show_line_numbers=True,
            show_line_marks=True,
            tab_width=4,
            monospace=True
        )
        print(self.__stack.to_json())
        source_buffer: GtkSource.Buffer = source_view.get_buffer()
        source_buffer.set_text(self.__stack.to_json(), -1)

        scrolled.set_child(source_view)
        self.set_start_child(scrolled)

    @property
    def aid(self) -> UUID:
        return self.__aid
