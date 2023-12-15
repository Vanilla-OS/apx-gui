# entry_subsystem.py
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

from gi.repository import Gtk, Adw
from typing import Text
from uuid import UUID

from apx_gui.core.apx_entities import Subsystem


@Gtk.Template(resource_path="/org/vanillaos/apx-gui/gtk/entry-subsystem.ui")
class EntrySubsystem(Adw.ActionRow):
    __gtype_name__: Text = "EntrySubsystem"

    def __init__(self, subsystem: Subsystem, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_title(subsystem.name)
        self.set_subtitle(f"Based on the {subsystem.stack.name} stack.")

        self.subsystem: Subsystem = subsystem
        self.aid: UUID = subsystem.aid
