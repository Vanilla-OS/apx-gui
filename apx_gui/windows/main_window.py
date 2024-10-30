# main_window.py
#
# Copyright 2024 Mirko Brombin
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

import yaml
from typing import Any
from uuid import UUID
from gi.repository import Gtk, Adw, GLib, Gio  # pyright: ignore
from gettext import gettext as _

from apx_gui.core.apx import Apx
from apx_gui.core.apx_entities import Subsystem, Stack, PkgManager
from apx_gui.core.monitor import Monitor
from apx_gui.core.run_async import RunAsync
from apx_gui.widgets.editor import Editor
from apx_gui.widgets.sidebar import Sidebar
from apx_gui.windows.create_subsystem import CreateSubsystemWindow
from apx_gui.windows.create_stack import CreateStackWindow
from apx_gui.windows.create_pkgmanager import CreatePkgManagerWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/window-main.ui")
class ApxGUIWindow(Adw.ApplicationWindow):
    __gtype_name__: str = "ApxGUIWindow"

    toasts: Adw.ToastOverlay = Gtk.Template.Child()  # pyright: ignore
    paned_main: Adw.OverlaySplitView = Gtk.Template.Child()  # pyright: ignore
    content: Adw.Bin = Gtk.Template.Child()  # pyright: ignore
    tab_bar: Adw.TabBar = Gtk.Template.Child()  # pyright: ignore
    title: Adw.WindowTitle = Gtk.Template.Child()  # pyright: ignore
    style_manager = Adw.StyleManager().get_default()  # pyright: ignore

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.__apx: Apx = Apx()
        self.__subsystems: list[Subsystem] = self.__apx.subsystems_list()
        self.__stacks: list[Stack] = self.__apx.stacks_list()
        self.__pkgmanagers: list[PkgManager] = self.__apx.pkgmanagers_list()

        GLib.timeout_add_seconds(2, self.__read_changes)

        self.__build_ui()

    def __build_ui(self) -> None:
        self.editor: Editor = Editor(self)
        self.content.set_child(self.editor)
        self.tab_bar.set_view(self.editor.tabs_editor)

        self.sidebar: Sidebar = Sidebar(
            self, self.__subsystems, self.__stacks, self.__pkgmanagers
        )
        self.paned_main.set_sidebar(self.sidebar)

    def __read_changes(self) -> bool:
        def callback(events: list[dict[str, Any]], exception: Exception):
            try:
                for event in events:
                    for subsystem in self.__subsystems:
                        if event["Actor"]["Attributes"]["name"] == "apx-" + subsystem.name:
                            if event["status"] == "start":
                                subsystem.status = "Up"
                            elif event["status"] == "die":
                                subsystem.status = "Exited"

                            self.sidebar.update_subsystem(subsystem)
                            self.editor.update_subsystem_tab(subsystem)
                            break
            except TypeError:
                print("No new events queue.  Skipping UI refresh...")

        RunAsync(Monitor.read, callback)
        return True

    def toast(self, message: str, timeout: int = 2) -> Adw.Toast:
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

    def remove_subsystem(self, aid: UUID, subsystem: Subsystem) -> None:
        self.editor.close(aid)
        self.sidebar.remove_subsystem(aid)
        self.__subsystems.remove(subsystem)

    def remove_stack(self, aid: UUID, stack: Stack) -> None:
        self.editor.close(aid)
        self.sidebar.remove_stack(aid)
        self.__stacks.remove(stack)

    def remove_pkgmanager(self, aid: UUID, pkgmanager: PkgManager) -> None:
        self.editor.close(aid)
        self.sidebar.remove_pkgmanager(aid)
        self.__pkgmanagers.remove(pkgmanager)

    def new_subsystem(self) -> None:
        window: CreateSubsystemWindow = CreateSubsystemWindow(
            self, self.__subsystems, self.__stacks
        )
        window.show()

    def new_stack(self) -> None:
        window: CreateStackWindow = CreateStackWindow(
            self, self.__stacks, self.__pkgmanagers
        )
        window.show()

    def new_pkgmanager(self) -> None:
        window: CreatePkgManagerWindow = CreatePkgManagerWindow(
            self, self.__pkgmanagers
        )
        window.show()

    def import_file(self) -> None:
        file_picker = Gtk.FileDialog()
        file_filters = Gio.ListStore.new(Gtk.FileFilter)

        yaml_filter = Gtk.FileFilter()
        yaml_filter.add_pattern("*.yml")
        yaml_filter.add_pattern("*.yaml")

        yaml_filter.set_name(_("YAML Files"))
        file_filters.append(yaml_filter)

        file_picker.set_title("Import a YAML File")
        file_picker.set_filters(file_filters)
        file_picker.open(parent=self, cancellable=None, callback=self.open_file_callback)

    def open_file_callback(self, filedialog, task):
        try:
            file = filedialog.open_finish(task)
            with open(file.get_path()) as imported_file:
                contents = yaml.load(imported_file, Loader=yaml.SafeLoader)

                try:
                    entity: PkgManager = PkgManager(
                        contents["name"],
                        contents["needsudo"],
                        contents["cmdautoremove"],
                        contents["cmdclean"],
                        contents["cmdinstall"],
                        contents["cmdlist"],
                        contents["cmdpurge"],
                        contents["cmdremove"],
                        contents["cmdsearch"],
                        contents["cmdshow"],
                        contents["cmdupdate"],
                        contents["cmdupgrade"],
                        False,
                    )
                    result = entity.create()
                    if result[0]:
                        self.append_pkgmanager(result[1])
                        self.toast(_("Package manager {} created successfully").format(entity.name))
                        return
                except KeyError:
                    print("Package manager not detected in import.")
                except Exception as e:
                    print(e)

                try:
                    for pkgmanager in self.__pkgmanagers:
                        if pkgmanager.name == contents["pkgmanager"]:
                            entity: Stack = Stack(
                                contents["name"],
                                contents["base"],
                                contents["packages"],
                                contents["pkgmanager"],
                                False,
                            )
                            result = entity.create()
                            if result[0]:
                                self.append_stack(result[1])
                                self.toast(_("Stack {} created successfully").format(stack.name))
                                return
                except KeyError:
                    print("Stack not detected in import.")
                except Exception as e:
                    print(e)

        except GLib.GError:
            return
        
        self.toast(_("File import failed."))
