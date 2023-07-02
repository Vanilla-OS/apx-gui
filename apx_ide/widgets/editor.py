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

from apx_ide.widgets.tab_subsystem import TabSubsystem
from apx_ide.core.apx_entities import Subsystem


@Gtk.Template(resource_path='/org/vanillaos/apx-ide/gtk/editor.ui')
class Editor(Adw.Bin):
    __gtype_name__ = 'Editor'
    __registry__ = {
        "open": [],
        "tabs": {},
    }

    tabs_editor = Gtk.Template.Child()
    stack_editor = Gtk.Template.Child()
    page_no_tabs = Gtk.Template.Child()
    page_editor = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__build_ui()

    def __build_ui(self):
        self.tabs_editor.connect('page-detached', self.__on_page_detached)
        self.tabs_editor.connect('page-attached', self.__on_page_attached)

    def __on_page_detached(self, tabs, page, *args):
        self.__registry__["open"].remove(page.get_child().aid)
        self.__registry__["tabs"].pop(page.get_child().aid)

        if tabs.get_n_pages() == 0:
            self.stack_editor.set_visible_child_name('no_tabs')

    def __on_page_attached(self, tabs, page, *args):
        self.page_no_tabs.set_visible(False)
        self.page_editor.set_visible(True)
        self.__registry__["open"].append(page.get_child().aid)
        self.__registry__["tabs"][page.get_child().aid] = page

        if tabs.get_n_pages() > 0:
            self.stack_editor.set_visible_child_name('editor')
        
    def open(self, aid):
        if aid in self.__registry__["open"]:
            self.tabs_editor.set_selected_page(self.__registry__["tabs"][aid])
            return True
        return False

    def is_open(self, aid):
        return aid in self.__registry__["open"]
    
    def new_subsystem_tab(self, subsystem: Subsystem):
        page = self.tabs_editor.append(TabSubsystem(subsystem))
        page.set_title(subsystem.name)
        self.open(subsystem.aid)
