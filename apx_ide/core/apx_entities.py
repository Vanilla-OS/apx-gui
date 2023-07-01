import subprocess
import shlex
import json
import uuid

from apx_ide.core.apx_exceptions import ApxCommandError, ApxCreationError, ApxUpdateError, ApxDeletionError


class ApxEntityBase:
    def __init__(self):
        self.aid = uuid.uuid4()

    def _run_command(self, command):
        try:
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if process.returncode != 0:
                error_message = error.decode('utf-8').strip()
                raise ApxCommandError(f"Command execution failed: {error_message}")
            return output.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            raise ApxCommandError(f"Command execution failed: {e}")


class Subsystem(ApxEntityBase):
    def __init__(self, internal_name, name, stack, status):
        super().__init__()
        self.internal_name = internal_name
        self.name = name
        self.stack = stack
        self.status = status

    def create(self, stack):
        command = f"apx2 subsystems new --name {self.name} --stack {stack}"
        output = self._run_command(command)
        if not output:
            raise ApxCreationError(f"Failed to create Subsystem {self.name}")

    def update(self, stack):
        command = f"apx2 subsystems update --name {self.internal_name} --stack {stack}"
        output = self._run_command(command)
        if not output:
            raise ApxUpdateError(f"Failed to update Subsystem {self.internal_name}")

    def remove(self, force=False):
        force_flag = "--force" if force else ""
        command = f"apx2 subsystems rm {force_flag} --name {self.internal_name}"
        output = self._run_command(command)
        if not output:
            raise ApxDeletionError(f"Failed to remove Subsystem {self.internal_name}")


class Stack(ApxEntityBase):
    def __init__(self, name, base, packages, pkg_manager, built_in):
        super().__init__()
        self.name = name
        self.base = base
        self.packages = packages
        self.pkg_manager = pkg_manager
        self.built_in = built_in

    def create(self, base, packages, pkg_manager):
        command = f"apx2 stacks new --name {self.name} --base {base} --packages {packages} --pkg-manager {pkg_manager}"
        output = self._run_command(command)
        if not output:
            raise ApxCreationError(f"Failed to create Stack {self.name}")

    def update(self, base, packages, pkg_manager):
        command = f"apx2 stacks update --name {self.name} --base {base} --packages {packages} --pkg-manager {pkg_manager}"
        output = self._run_command(command)
        if not output:
            raise ApxUpdateError(f"Failed to update Stack {self.name}")

    def remove(self, force=False):
        force_flag = "--force" if force else ""
        command = f"apx2 stacks rm {force_flag} --name {self.name}"
        output = self._run_command(command)
        if not output:
            raise ApxDeletionError(f"Failed to remove Stack {self.name}")


class PkgManager(ApxEntityBase):
    def __init__(self, name, need_sudo, cmd_auto_remove, cmd_clean, cmd_install, cmd_list, cmd_purge, cmd_remove,
                 cmd_search, cmd_show, cmd_update, cmd_upgrade, built_in):
        super().__init__()
        self.name = name
        self.need_sudo = need_sudo
        self.cmd_auto_remove = cmd_auto_remove
        self.cmd_clean = cmd_clean
        self.cmd_install = cmd_install
        self.cmd_list = cmd_list
        self.cmd_purge = cmd_purge
        self.cmd_remove = cmd_remove
        self.cmd_search = cmd_search
        self.cmd_show = cmd_show
        self.cmd_update = cmd_update
        self.cmd_upgrade = cmd_upgrade
        self.built_in = built_in

    def create(self, name, need_sudo, cmd_auto_remove, cmd_clean, cmd_install, cmd_list, cmd_purge, cmd_remove,
               cmd_search, cmd_show, cmd_update, cmd_upgrade):
        command = f"apx2 pkgmanagers new --name {name} --need-sudo {need_sudo} --autoremove {cmd_auto_remove} " \
                  f"--clean {cmd_clean} --install {cmd_install} --list {cmd_list} --purge {cmd_purge} " \
                  f"--remove {cmd_remove} --search {cmd_search} --show {cmd_show} --update {cmd_update} " \
                  f"--upgrade {cmd_upgrade}"
        output = self._run_command(command)
        if not output:
            raise ApxCreationError(f"Failed to create PkgManager {name}")

    def remove(self):
        command = f"apx2 pkgmanagers rm --name {self.name}"
        output = self._run_command(command)
        if not output:
            raise ApxDeletionError(f"Failed to remove PkgManager {self.name}")
