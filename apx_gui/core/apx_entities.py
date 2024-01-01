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

import os
import subprocess
import shlex
import json
import uuid
from uuid import UUID
from typing import Optional, List, Dict, Union, Tuple, Text


class ApxEntityBase:
    def __init__(self) -> None:
        self.aid: UUID = uuid.uuid4()

    def _run_command(self, command: Text) -> Tuple[bool, str]:
        try:
            if "APX_DEBUG" in os.environ:
                print(f"Running command: {command}")

            process: subprocess.Popen = subprocess.Popen(
                shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output: bytes
            error: bytes
            output, error = process.communicate()
            if error:
                return False, error.decode("utf-8")
            return True, output.decode("utf-8")
        except Exception as e:
            return False, str(e)

    def to_dict(self) -> Dict[str, Union[str, UUID]]:
        return self.__dict__

    def to_json(self) -> str:
        obj = self.to_dict().copy()
        obj.pop("aid", None)
        return json.dumps(obj, indent=4)


class Stack(ApxEntityBase):
    def __init__(
        self,
        name: Text,
        base: Text,
        packages: Union[str, List[str]],
        pkg_manager: Text,
        built_in: Text,
    ) -> None:
        super().__init__()
        self.name: Text = name
        self.base: Text = base
        self.packages: Union[str, List[str]] = packages
        self.pkg_manager: Text = pkg_manager
        self.built_in: Text = built_in

    def create(self) -> Tuple[bool, "Stack"]:
        packages: Text = (
            " ".join(self.packages)
            if isinstance(self.packages, list)
            else self.packages
        )
        command: Text = (
            f'apx stacks new --name {self.name} --base {self.base} --packages "{packages}" '
            f"--pkg-manager {self.pkg_manager} -y"
        )
        res: Tuple[bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        command: Text = f"apx stacks list --json"
        res: Tuple[bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        stacks: List[Dict[str, str]] = json.loads(res[1])
        for stack in stacks:
            if stack["Name"] == self.name:
                self.base = stack["Base"]
                self.packages = stack["Packages"]
                self.pkg_manager = stack["PkgManager"]
                self.built_in = stack["BuiltIn"]
                return True, self

        return False, self

    def update(self, base: Text, packages: Text, pkg_manager: Text) -> Tuple[bool, str]:
        command: Text = f'apx stacks update --name {self.name} --base {base} --packages "{packages}" --pkg-manager {pkg_manager} -y'
        return self._run_command(command)

    def remove(self, force: bool = False) -> Tuple[bool, str]:
        force_flag: Text = "--force" if force else ""
        command: Text = f"apx stacks rm {force_flag} --name {self.name}"
        return self._run_command(command)


class Subsystem(ApxEntityBase):
    def __init__(
        self,
        internal_name: Text,
        name: Text,
        stack: Stack,
        status: Text,
        enter_command: List[str],
        exported_programs: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self.internal_name: Text = internal_name
        self.name: Text = name
        self.stack: Stack = stack
        self.status: Text = status
        self.enter_command: List[str] = enter_command
        self.exported_programs: Optional[Dict[str, str]] = exported_programs

    def create(self) -> Tuple[bool, "Subsystem"]:
        command: Text = (
            f"apx subsystems new --name {self.name} --stack {self.stack.name}"
        )
        res: Tuple[bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        command: Text = f"apx subsystems list --json"
        res: Tuple[bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        subsystems: List[Dict[str, str]] = json.loads(res[1])
        for subsystem in subsystems:
            if subsystem["Name"] == self.name:
                self.internal_name = subsystem["InternalName"]
                self.status = subsystem["Status"]
                self.exported_programs = subsystem["ExportedPrograms"]
                return True, self

        return False, self

    def update(self, stack: Text) -> Tuple[bool, str]:
        command: Text = f"apx subsystems update --name {self.name} --stack {stack} -y"
        return self._run_command(command)

    def remove(self, force: bool = False) -> Tuple[bool, str]:
        force_flag: Text = "--force" if force else ""
        command: Text = f"apx subsystems rm {force_flag} --name {self.name}"
        return self._run_command(command)

    def reset(self, force: bool = False) -> Tuple[bool, str]:
        force_flag: Text = "--force" if force else ""
        command: Text = f"apx subsystems reset {force_flag} --name {self.name}"
        return self._run_command(command)


class PkgManager(ApxEntityBase):
    def __init__(
        self,
        name: Text,
        need_sudo: bool,
        cmd_auto_remove: Text,
        cmd_clean: Text,
        cmd_install: Text,
        cmd_list: Text,
        cmd_purge: Text,
        cmd_remove: Text,
        cmd_search: Text,
        cmd_show: Text,
        cmd_update: Text,
        cmd_upgrade: Text,
        built_in: Text,
    ) -> None:
        super().__init__()
        self.name: Text = name
        self.need_sudo: bool = need_sudo
        self.cmd_auto_remove: Text = cmd_auto_remove
        self.cmd_clean: Text = cmd_clean
        self.cmd_install: Text = cmd_install
        self.cmd_list: Text = cmd_list
        self.cmd_purge: Text = cmd_purge
        self.cmd_remove: Text = cmd_remove
        self.cmd_search: Text = cmd_search
        self.cmd_show: Text = cmd_show
        self.cmd_update: Text = cmd_update
        self.cmd_upgrade: Text = cmd_upgrade
        self.built_in: Text = built_in

    def create(self) -> Tuple[bool, "PkgManager"]:
        command: Text = (
            f"apx pkgmanagers new --name {self.name} --need-sudo {self.need_sudo} "
            f"--autoremove {self.cmd_auto_remove} --clean {self.cmd_clean} "
            f"--install {self.cmd_install} --list {self.cmd_list} "
            f"--purge {self.cmd_purge} --remove {self.cmd_remove} "
            f"--search {self.cmd_search} --show {self.cmd_show} "
            f"--update {self.cmd_update} --upgrade {self.cmd_upgrade}"
        )
        res: Tuple[bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        command: Text = f"apx pkgmanagers list --json"
        res: Tuple[bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        pkgmanagers: List[Dict[str, Union[str, bool]]] = json.loads(res[1])
        for pkgmanager in pkgmanagers:
            if pkgmanager["Name"] == self.name:
                self.need_sudo = pkgmanager["NeedSudo"]
                self.cmd_auto_remove = pkgmanager["CmdAutoRemove"]
                self.cmd_clean = pkgmanager["CmdClean"]
                self.cmd_install = pkgmanager["CmdInstall"]
                self.cmd_list = pkgmanager["CmdList"]
                self.cmd_purge = pkgmanager["CmdPurge"]
                self.cmd_remove = pkgmanager["CmdRemove"]
                self.cmd_search = pkgmanager["CmdSearch"]
                self.cmd_show = pkgmanager["CmdShow"]
                self.cmd_update = pkgmanager["CmdUpdate"]
                self.cmd_upgrade = pkgmanager["CmdUpgrade"]
                self.built_in = pkgmanager["BuiltIn"]
                return True, self

        return False, self

    def remove(self, force: bool = False) -> Tuple[bool, str]:
        force_flag: Text = "--force" if force else ""
        command: Text = f"apx pkgmanagers rm {force_flag} --name {self.name}"
        return self._run_command(command)

    def update(
        self,
        need_sudo: bool,
        cmd_auto_remove: Text,
        cmd_clean: Text,
        cmd_install: Text,
        cmd_list: Text,
        cmd_purge: Text,
        cmd_remove: Text,
        cmd_search: Text,
        cmd_show: Text,
        cmd_update: Text,
        cmd_upgrade: Text,
    ) -> Tuple[bool, str]:
        command: Text = (
            f"apx pkgmanagers update --name {self.name} --need-sudo {need_sudo} "
            f"--autoremove {cmd_auto_remove} --clean {cmd_clean} "
            f"--install {cmd_install} --list {cmd_list} "
            f"--purge {cmd_purge} --remove {cmd_remove} "
            f"--search {cmd_search} --show {cmd_show} "
            f"--update {cmd_update} --upgrade {cmd_upgrade}"
        )
        return self._run_command(command)
