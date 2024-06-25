# apx_entities.py
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

import os
import shutil
import subprocess
import shlex
import json
import uuid
from uuid import UUID

from typing import Any
from collections.abc import Callable
from gi.repository import Vte, GLib
from time import sleep


class ApxEntityBase:
    def __init__(self) -> None:
        self.aid: UUID = uuid.uuid4()

    def _is_running_in_container(self) -> bool:
        """
        Check if the program is running inside a container.
        """
        return os.path.exists("/run/.containerenv")

    def _get_apx_command(self) -> str:
        """
        Get the appropriate command for running 'apx' based on the
        environment.
        """
        if self._is_running_in_container():
            return f"{self.__host_spawn_bin} apx"
        else:
            return self.__apx_bin

    @property
    def __apx_bin(self) -> str:
        """
        Get the path to the 'apx' binary.
        """
        return shutil.which("apx") or "/usr/bin/apx"

    @property
    def __host_spawn_bin(self) -> str:
        """
        Get the path to the 'host_spawn' binary.
        """
        return shutil.which("host-spawn") or "/usr/bin/host-spawn"

    def _run_command(
        self, command: str, ignore_errors: bool = False
    ) -> tuple[bool, str]:
        try:
            if "APX_DEBUG" in os.environ:
                print(f"Running command: {command}")

            process: subprocess.Popen = subprocess.Popen(
                shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, e = process.communicate()
            output: str = out.decode("utf-8")
            error: str = e.decode("utf-8")
            if error and not ignore_errors:
                if "APX_DEBUG" in os.environ:
                    print(f"Error: {error}")
                return False, error
            if "APX_DEBUG" in os.environ:
                print(f"Output: {output}")
            return True, output
        except Exception as e:
            if "APX_DEBUG" in os.environ:
                print(f"Exception: {e}")
            return False, str(e)

    def _run_apx_command(
        self, args: str, ignore_errors: bool = False
    ) -> tuple[bool, str]:
        """
        Run the 'apx' command with the specified arguments.
        """
        command = f"{self._get_apx_command()} {args}"
        return self._run_command(command, ignore_errors)

    def to_dict(self) -> dict[str, str | UUID]:
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
        packages: str | list[str],
        pkg_manager: str,
        built_in: bool,
    ) -> None:
        super().__init__()
        self.name: str = name
        self.base: str = base
        self.packages: str | list[str] = packages
        self.pkg_manager: str = pkg_manager
        self.built_in: bool = built_in

    def create(self) -> tuple[bool, "Stack"]:
        packages: str = (
            " ".join(self.packages)
            if isinstance(self.packages, list)
            else self.packages
        )
        new_command: str = (
            f"apx stacks new --name '{self.name}' --base '{self.base}' --packages '{packages}' "
            f"--pkg-manager {self.pkg_manager} -y"
        )
        new_res: tuple[bool, str] = self._run_command(new_command)


        list_command: str = f"apx stacks list --json"
        list_res: tuple[bool, str] = self._run_command(list_command)
        if not list_res[0]:
            return list_res[0], self

        stacks = json.loads(list_res[1])
        for stack in stacks:
            if stack["Name"] == self.name:
                self.base = stack["Base"]
                self.packages = stack["Packages"]
                self.pkg_manager = stack["PkgManager"]
                self.built_in = stack["BuiltIn"]
                return True, self

        return False, self

    def update(self, base: str, packages: str, pkg_manager: str) -> tuple[bool, str]:
        command: str = (
            f"apx stacks update --name '{self.name}' --base '{base}' --packages '{packages}' --pkg-manager '{pkg_manager}' -y"
        )
        return self._run_command(command)

    def remove(self, force: bool = False) -> tuple[bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"apx stacks rm {force_flag} --name '{self.name}'"
        return self._run_command(command)


class Subsystem(ApxEntityBase):
    def __init__(
        self,
        internal_name: str,
        name: str,
        stack: Stack,
        status: str,
        enter_command: list[str],
        exported_programs: dict[str, dict[str, str]] | None = None,
    ) -> None:
        super().__init__()
        self.internal_name: str = internal_name
        self.name: str = name
        self.stack: Stack = stack
        self.status: str = status
        self.enter_command: list[str] = enter_command
        self.exported_programs: dict[str, dict[str, str]] = exported_programs or {}

    def create(
        self,
        _terminal,
    ) -> tuple[bool, "Subsystem"]:
        new_command = (
            f"{self._get_apx_command()}",
            "subsystems",
            "new",
            "--name",
            f"{self.name}",
            "--stack",
            f"{self.stack.name}",
        )
        # the following apx command is safe to ignore errors, we´ll check the
        # subsystem status by getting the list of subsystems
        self.run_vte_command(new_command, _terminal, self._Create_Callback)

    def _create_callback(self,*args):
        list_command: str = f"subsystems list --json"
        list_res: tuple[bool, str] = self._run_apx_command(list_command)
        if not list_res[0]:
            return list_res[0], self

        try:
            subsystems = json.loads(list_res[1])
        except json.decoder.JSONDecodeError:
            return False, self
        for subsystem in subsystems:
            if subsystem["Name"] == self.name:
                self.internal_name = subsystem["InternalName"]
                self.status = subsystem["Status"]
                self.exported_programs = subsystem["ExportedPrograms"]
                return True, self

        return False, self

    def run_vte_command(
        self,
        args,
        __terminal,
        __callbackfunc,
    ) -> tuple[bool, str]:
        """
        Run the 'apx' command with the specified arguments.
        """
        __terminal.connect("child-exited", __callbackfunc)
        Term = __terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            ".",
            args,
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            None,
        )

    @property
    def running(self) -> bool:
        return "Up" in self.status or "running" in self.status

    def start(self) -> tuple[bool, str]:
        command: str = f"{self.name} start"
        return self._run_apx_command(command)

    def stop(self) -> tuple[bool, str]:
        command: str = f"{self.name} stop"
        return self._run_apx_command(command)

    def update(self, stack: str) -> tuple[bool, str]:
        command: str = f"subsystems update --name '{self.name}' --stack '{stack}' -y"
        return self._run_apx_command(command)

    def remove(self, force: bool = False) -> tuple[bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"subsystems rm {force_flag} --name '{self.name}'"
        return self._run_apx_command(command)

    def reset(self, force: bool = False) -> tuple[bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"subsystems reset {force_flag} --name '{self.name}'"
        return self._run_apx_command(command)

    def autoremove(self) -> tuple[bool, str]:
        command: str = f"{self.name} autoremove"
        return self._run_apx_command(command)

    def clean(self) -> tuple[bool, str]:
        command: str = f"{self.name} clean"
        return self._run_apx_command(command)


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
        built_in: bool,
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
        self.built_in: bool = built_in

    def create(self) -> tuple[bool, "PkgManager"]:
        new_command: str = (
            f"pkgmanagers new --name '{self.name}' --need-sudo '{self.need_sudo}' "
            f"--autoremove '{self.cmd_auto_remove}' --clean '{self.cmd_clean}' "
            f"--install '{self.cmd_install}' --list '{self.cmd_list}' "
            f"--purge '{self.cmd_purge}' --remove '{self.cmd_remove}' "
            f"--search '{self.cmd_search}' --show '{self.cmd_show}' "
            f"--update '{self.cmd_update}' --upgrade '{self.cmd_upgrade}'"
        )
        new_res: tuple[bool, str] = self._run_apx_command(new_command)
        if not new_res[0]:
            return new_res[0], self

        list_command: str = f"pkgmanagers list --json"
        list_res: tuple[bool, str] = self._run_apx_command(list_command)
        if not list_res[0]:
            return list_res[0], self

        pkgmanagers = json.loads(list_res[1])
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

    def remove(self, force: bool = False) -> tuple[bool, str]:
        force_flag: str = "--force" if force else ""
        command: str = f"pkgmanagers rm {force_flag} --name '{self.name}'"
        return self._run_apx_command(command)

    def update(
        self,
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
    ) -> tuple[bool, str]:
        command: str = (
            f"pkgmanagers update --name '{self.name}' --need-sudo '{need_sudo}' "
            f"--autoremove '{cmd_auto_remove}' --clean '{cmd_clean}' "
            f"--install '{cmd_install}' --list '{cmd_list}' "
            f"--purge '{cmd_purge}' --remove '{cmd_remove}' "
            f"--search '{cmd_search}' --show '{cmd_show}' "
            f"--update '{cmd_update}' --upgrade '{cmd_upgrade}'"
        )
        return self._run_apx_command(command)

