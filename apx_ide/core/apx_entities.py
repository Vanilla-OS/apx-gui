# apx_entities.py
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

import subprocess
import shlex
import json
import uuid
from uuid import UUID
from typing import Optional

from apx_ide.core.apx_exceptions import ApxCommandError, ApxCreationError, ApxUpdateError, ApxDeletionError


class ApxEntityBase:
    def __init__(self):
        self.aid: UUID = uuid.uuid4()

    def _run_command(self, command: str) -> str:
        try:
            process: subprocess.Popen = subprocess.Popen(
                shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output: bytes
            error: bytes
            output, error = process.communicate()
            if process.returncode != 0:
                error_message: str = error.decode('utf-8').strip()
                raise ApxCommandError(f"Command execution failed: {error_message}")
            return output.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            raise ApxCommandError(f"Command execution failed: {e}")


class Stack(ApxEntityBase):
    def __init__(self, name: str, base: str, packages: str, pkg_manager: str, built_in: str):
        super().__init__()
        self.name: str = name
        self.base: str = base
        self.packages: str = packages
        self.pkg_manager: str = pkg_manager
        self.built_in: str = built_in

    def create(self, base: str, packages: str, pkg_manager: str) -> None:
        command: str = (
            f"apx2 stacks new --name {self.name} --base {base} --packages {packages} --pkg-manager {pkg_manager}"
        )
        output: str = self._run_command(command)
        if not output:
            raise ApxCreationError(f"Failed to create Stack {self.name}")

    def update(self, base: str, packages: str, pkg_manager: str) -> None:
        command: str = (
            f"apx2 stacks update --name {self.name} --base {base} --packages {packages} --pkg-manager {pkg_manager}"
        )
        output: str = self._run_command(command)
        if not output:
            raise ApxUpdateError(f"Failed to update Stack {self.name}")

    def remove(self, force: bool = False) -> None:
        force_flag: str = "--force" if force else ""
        command: str = f"apx2 stacks rm {force_flag} --name {self.name}"
        output: str = self._run_command(command)
        if not output:
            raise ApxDeletionError(f"Failed to remove Stack {self.name}")


class Subsystem(ApxEntityBase):
    def __init__(self, internal_name: str, name: str, stack: Stack, status: str):
        super().__init__()
        self.internal_name: str = internal_name
        self.name: str = name
        self.stack: Stack = stack
        self.status: str = status

    def create(self, stack: str) -> None:
        command: str = f"apx2 subsystems new --name {self.name} --stack {stack}"
        output: str = self._run_command(command)
        if not output:
            raise ApxCreationError(f"Failed to create Subsystem {self.name}")

    def update(self, stack: str) -> None:
        command: str = f"apx2 subsystems update --name {self.internal_name} --stack {stack}"
        output: str = self._run_command(command)
        if not output:
            raise ApxUpdateError(f"Failed to update Subsystem {self.internal_name}")

    def remove(self, force: bool = False) -> None:
        force_flag: str = "--force" if force else ""
        command: str = f"apx2 subsystems rm {force_flag} --name {self.internal_name}"
        output: str = self._run_command(command)
        if not output:
            raise ApxDeletionError(f"Failed to remove Subsystem {self.internal_name}")


class PkgManager(ApxEntityBase):
    def __init__(
        self,
        name: str,
        need_sudo: bool,
        cmd_auto_remove: str,
        cmd_clean: str,
        cmd_install: str,
        cmd_list: str,
        cmd_purge: str,
        cmd_remove: str,
        cmd_search: str,
        cmd_show: str,
        cmd_update: str,
        cmd_upgrade: str,
        built_in: str,
    ):
        super().__init__()
        self.name: str = name
        self.need_sudo: bool = need_sudo
        self.cmd_auto_remove: str = cmd_auto_remove
        self.cmd_clean: str = cmd_clean
        self.cmd_install: str = cmd_install
        self.cmd_list: str = cmd_list
        self.cmd_purge: str = cmd_purge
        self.cmd_remove: str = cmd_remove
        self.cmd_search: str = cmd_search
        self.cmd_show: str = cmd_show
        self.cmd_update: str = cmd_update
        self.cmd_upgrade: str = cmd_upgrade
        self.built_in: str = built_in

    def create(
        self,
        name: str,
        need_sudo: bool,
        cmd_auto_remove: str,
        cmd_clean: str,
        cmd_install: str,
        cmd_list: str,
        cmd_purge: str,
        cmd_remove: str,
        cmd_search: str,
        cmd_show: str,
        cmd_update: str,
        cmd_upgrade: str,
    ) -> None:
        command: str = (
            f"apx2 pkgmanagers new --name {name} --need-sudo {need_sudo} --autoremove {cmd_auto_remove} "
            f"--clean {cmd_clean} --install {cmd_install} --list {cmd_list} --purge {cmd_purge} "
            f"--remove {cmd_remove} --search {cmd_search} --show {cmd_show} --update {cmd_update} "
            f"--upgrade {cmd_upgrade}"
        )
        output: str = self._run_command(command)
        if not output:
            raise ApxCreationError(f"Failed to create PkgManager {name}")

    def remove(self) -> None:
        command: str = f"apx2 pkgmanagers rm --name {self.name}"
        output: str = self._run_command(command)
        if not output:
            raise ApxDeletionError(f"Failed to remove PkgManager {self.name}")
