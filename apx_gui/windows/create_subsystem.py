# create_subsystem.py
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
# SPDX-License-Identifier: GPL-3.0-only

from gi.repository import Gtk, Adw, Vte, Gdk  # pyright: ignore
from gettext import gettext as _

from apx_gui.core.apx_entities import Subsystem, Stack
from apx_gui.utils.gtk import GtkUtils
from apx_gui.core.run_async import RunAsync

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apx_gui.windows.main_window import ApxGUIWindow


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/create-subsystem.ui")
class CreateSubsystemWindow(Adw.Window):
    __gtype_name__ = "CreateSubsystemWindow"

    btn_cancel: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_close: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    btn_create: Gtk.Button = Gtk.Template.Child()  # pyright: ignore
    row_name: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    row_stack: Adw.ComboRow = Gtk.Template.Child()  # pyright: ignore
    row_home: Adw.EntryRow = Gtk.Template.Child()  # pyright: ignore
    str_stack: Gtk.StringList = Gtk.Template.Child()  # pyright: ignore
    stack_main: Adw.ViewStack = Gtk.Template.Child()  # pyright: ignore
    console_button: Gtk.Box = Gtk.Template.Child()  # pyright: ignore
    console_box: Gtk.Box = Gtk.Template.Child()  # pyright: ignore
    console_output: Gtk.Box = Gtk.Template.Child()  # pyright: ignore

    def __init__(
        self,
        window: Adw.ApplicationWindow,
        subsystems: list[Subsystem],
        stacks: list[Stack],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.__window: ApxGUIWindow = window  # pyright: ignore
        self.__subsystems: list[Subsystem] = subsystems
        self.__stacks: list[Stack] = stacks
        self.__terminal = Vte.Terminal()
        self.__style_manager = self.__window.style_manager

        self.console_box_visible = False

        self.__build_ui()
        self.__on_setup_terminal_colors()

    def __build_ui(self) -> None:
        self.set_transient_for(self.__window)

        for stack in self.__stacks:
            self.str_stack.append(stack.name)
        self.row_stack.set_selected(0)

        self.btn_cancel.connect("clicked", self.__on_cancel_clicked)
        self.btn_close.connect("clicked", self.__on_cancel_clicked)
        self.btn_create.connect("clicked", self.__on_create_clicked)
        self.console_button.connect("clicked", self.__on_console_button)
        self.row_name.connect("changed", self.__on_name_changed)
        self.row_home.connect("changed", self.__on_home_changed)
        self.console_output.append(self.__terminal)
        self.__terminal.connect("child-exited", self.on_vte_child_exited)

        self.__terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        self.__terminal.set_mouse_autohide(True)
        self.__terminal.set_input_enabled(False)

    def __on_setup_terminal_colors(self, *args):

        is_dark: bool = self.__style_manager.get_dark()

        palette = [
            "#363636",
            "#c01c28",
            "#26a269",
            "#a2734c",
            "#12488b",
            "#a347ba",
            "#2aa1b3",
            "#cfcfcf",
            "#5d5d5d",
            "#f66151",
            "#33d17a",
            "#e9ad0c",
            "#2a7bde",
            "#c061cb",
            "#33c7de",
            "#ffffff",
        ]

        FOREGROUND = palette[0]
        BACKGROUND = palette[15]
        FOREGROUND_DARK = palette[15]
        BACKGROUND_DARK = palette[0]

        self.fg = Gdk.RGBA()
        self.bg = Gdk.RGBA()

        self.colors = [Gdk.RGBA() for c in palette]
        [color.parse(s) for (color, s) in zip(self.colors, palette)]

        if is_dark:
            self.fg.parse(FOREGROUND_DARK)
            self.bg.parse(BACKGROUND_DARK)
        else:
            self.fg.parse(FOREGROUND)
            self.bg.parse(BACKGROUND)

        self.__terminal.set_colors(self.fg, self.bg, self.colors)

    def __on_cancel_clicked(self, button: Gtk.Button) -> None:
        self.close()

    def __on_console_button(self, *args):
        self.console_box_visible = not self.console_box_visible
        self.console_box.set_visible(self.console_box_visible)

        if not self.console_box_visible:
            self.set_default_size(540, 250)
        else:
            self.set_default_size(540, 500)

        # Prevents window jumping around
        self.maximize()
        self.unmaximize()

    def __on_create_clicked(self, button: Gtk.Button) -> None:
        button.set_visible(False)
        self.stack_main.set_visible_child_name("creating")
        self.set_default_size(540, 250)

        subsystem: Subsystem = Subsystem(
            "",
            self.row_name.get_text(),
            self.__stacks[self.row_stack.get_selected()],
            self.row_home.get_text(),
            "",
            [],
            {},
        )
        res, subsystem = subsystem.create(self.__terminal)
        if not res:
            self.stack_main.set_visible_child_name("error")
            return

        self.new_subsystem = subsystem

    def on_vte_child_exited(self, terminal, status, *args):
        terminal.get_parent().remove(terminal)
        status = not bool(status)

        if status:
            self.__window.append_subsystem(self.new_subsystem)
            self.close()
            self.__window.toast(
                _("Subsystem {} created successfully").format(self.new_subsystem.name)
            )
            return

        self.stack_main.set_visible_child_name("error")

    def __on_name_changed(self, entry: Adw.EntryRow) -> None:
        name: str = entry.get_text()
        if " " in name:
            cursor_position = entry.get_position()
            entry.set_text(name.replace(" ", "_"))
            entry.set_position(cursor_position)
        elif name in [subsystem.name for subsystem in self.__subsystems]:
            entry.add_css_class("error")
            self.btn_create.set_sensitive(False)
            return

        entry.remove_css_class("error")
        self.btn_create.set_sensitive(GtkUtils.validate_entry(entry))

    def __on_home_changed(self, entry: Adw.EntryRow) -> None:
        if GtkUtils.validate_path_entry(entry):
            self.btn_create.set_sensitive(GtkUtils.validate_entry(self.row_name))
        else:
            self.btn_create.set_sensitive(False)
