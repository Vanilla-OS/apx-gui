import subprocess
import shlex
import json

from apx_ide.core.apx_exceptions import ApxCommandError, ApxCreationError, ApxUpdateError, ApxDeletionError
from apx_ide.core.apx_entities import ApxEntityBase, Subsystem, Stack, PkgManager


class Apx(ApxEntityBase):
    def __init__(self):
        pass

    def subsystems_list(self):
        command = "apx2 subsystems list --json"
        output = self._run_command(command)
        subsystems_data = json.loads(output)
        subsystems = []

        for data in subsystems_data:
            stack = Stack(
                data["Name"], 
                data["Stack"]["Base"],
                data["Stack"]["Packages"],
                data["Stack"]["PkgManager"],
                data["Stack"]["BuiltIn"]
            )
            subsystem = Subsystem(
                data["InternalName"],
                data["Name"], 
                stack, 
                data["Status"]
            )
            subsystems.append(subsystem)

        return subsystems

    def stacks_list(self):
        command = "apx2 stacks list --json"
        output = self._run_command(command)
        stacks_data = json.loads(output)
        stacks = []

        for data in stacks_data:
            stack = Stack(
                data["Name"], 
                data["Base"], 
                data["Packages"], 
                data["PkgManager"], 
                data["BuiltIn"]
            )
            stacks.append(stack)

        return stacks

    def pkgmanagers_list(self):
        command = "apx2 pkgmanagers list --json"
        output = self._run_command(command)
        pkgmanagers_data = json.loads(output)
        pkgmanagers = []

        for data in pkgmanagers_data:
            pkgmanager = PkgManager(
                data["Name"], 
                data["NeedSudo"], 
                data["AutoRemove"], 
                data["Clean"],
                ata["Install"], 
                data["List"], 
                data["Purge"], 
                data["Remove"], 
                data["Search"],
                data["Show"], 
                data["Update"], 
                data["Upgrade"], 
                data["BuiltIn"]
            ) 
            pkgmanagers.append(pkgmanager)

        return pkgmanagers
