# gtk.py
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

from gi.repository import Adw

import re
from functools import wraps
from inspect import signature

from gi.repository import GLib


class GtkUtils:

    @staticmethod
    def validate_entry(entry: Adw.EntryRow, extend=None) -> bool:
        text: str = entry.get_text()
        if re.search("[@!#$%^&*()<>?/|}{~:.;,'\"]", text) or len(text) == 0 or text.isspace():
            entry.add_css_class("error")
            return False

        if extend is not None:
            if extend(text):
                entry.add_css_class("error")
                return False

        entry.remove_css_class("error")
        return True