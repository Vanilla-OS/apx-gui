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
from typing import Optional


class ApxEntityBase:
    def __init__(self) -> None:
        self.aid: UUID = uuid.uuid4()

    def _run_command(self, command: str) -> [bool, str]:
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
    
    def to_dict(self) -> dict:
        return self.__dict__

    def to_json(self) -> str:
        obj = self.to_dict().copy()
        obj.pop("aid", None)
        return json.dumps(obj, indent=4)


class Stack(ApxEntityBase):
    def __init__(
        self, 
        name: str, 
        base: str, 
        packages: str, 
        pkg_manager: str, 
        built_in: str
    ) -> None:
        super().__init__()
        self.name: str = name
        self.base: str = base
        self.packages: str = packages
        self.pkg_manager: str = pkg_manager
        self.built_in: str = built_in

    def create(self) -> [bool, "Stack"]:
        packages: str = " ".join(self.packages) if isinstance(self.packages, list) else self.packages
        command: str = (
            f"apx2 stacks new --name {self.name} --base {self.base} --packages {packages} "
            f"--pkg-manager {self.pkg_manager}"
        )
        res: [bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        command: str = f"apx2 stacks list --json"
        res: [bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        stacks: list[dict] = json.loads(res[1])
        for stack in stacks:
            if stack["Name"] == self.name:
                self.base = stack["Base"]
                self.packages = stack["Packages"]
                self.pkg_manager = stack["PkgManager"]
                self.built_in = stack["BuiltIn"]
                return True, self

        return False, self

    def update(self, base: str, packages: str, pkg_manager: str) -> [bool, str]:
        command: str = (
            f"apx2 stacks update --name {self.name} --base {base} --packages {packages} --pkg-manager {pkg_manager} -y"
        )
        return self._run_command(command)

    def remove(self, force: bool = False) -> [bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"apx2 stacks rm {force_flag} --name {self.name}"
        return self._run_command(command)


class Subsystem(ApxEntityBase):
    def __init__(
        self, 
        internal_name: str, 
        name: str, 
        stack: Stack, 
        status: str, 
        exported_programs: Optional[dict] = None
    ) -> None:
        super().__init__()
        self.internal_name: str = internal_name
        self.name: str = name
        self.stack: Stack = stack
        self.status: str = status
        self.exported_programs: Optional[dict] = exported_programs

    def create(self) -> [bool, "Subsystem"]:
        command: str = f"apx2 subsystems new --name {self.name} --stack {self.stack.name}"
        res: [bool, str] = self._run_command(command)
        if not res[0]:
            return re[0], self

        command: str = f"apx2 subsystems list --json"
        res: [bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        subsystems: list[dict] = json.loads(res[1])
        for subsystem in subsystems:
            if subsystem["Name"] == self.name:
                self.internal_name = subsystem["InternalName"]
                self.status = subsystem["Status"]
                self.exported_programs = subsystem["ExportedPrograms"]
                return True, self

        return False, self

    def update(self, stack: str) -> [bool, str]:
        command: str = f"apx2 subsystems update --name {self.name} --stack {stack} -y"
        return self._run_command(command)

    def remove(self, force: bool = False) -> [bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"apx2 subsystems rm {force_flag} --name {self.name}"
        return self._run_command(command)

    def reset(self, force: bool = False) -> [bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"apx2 subsystems reset {force_flag} --name {self.name}"
        return self._run_command(command)


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
    ) -> None:
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

    def create(self) -> [bool, "PkgManager"]:
        command: str = (
            f"apx2 pkgmanagers new --name {self.name} --need-sudo {self.need_sudo} "
            f"--autoremove {self.cmd_auto_remove} --cmd-clean {self.cmd_clean} "
            f"--install {self.cmd_install} --list {self.cmd_list} "
            f"--purge {self.cmd_purge} --remove {self.cmd_remove} "
            f"--search {self.cmd_search} --show {self.cmd_show} "
            f"--update {self.cmd_update} --upgrade {self.cmd_upgrade}"
        )
        res: [bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        command: str = f"apx2 pkgmanagers list --json"
        res: [bool, str] = self._run_command(command)
        if not res[0]:
            return res[0], self

        pkgmanagers: list[dict] = json.loads(res[1])
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

    def remove(self, force: bool = False) -> [bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"apx2 pkgmanagers rm {force_flag} --name {self.name}"
        return self._run_command(command)