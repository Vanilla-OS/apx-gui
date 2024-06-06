# apx.py
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

import json
import requests
import socket

from typing import Any

from datetime import datetime, UTC
from requests.adapters import HTTPAdapter

from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from urllib3.util import Retry


class SocketConnection(HTTPConnection):
    def __init__(self, sock_addr):
        self.__sock_addr = sock_addr
        super().__init__("localhost")

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.__sock_addr)


class SocketConnectionPool(HTTPConnectionPool):
    def __init__(self, sock_addr: str):
        self.__sock_addr = sock_addr
        super().__init__("localhost")

    def _new_conn(self):
        return SocketConnection(self.__sock_addr)


class SocketAdapter(HTTPAdapter):
    def __init__(
        self,
        sock_addr: str,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: Retry | int | None = 0,
        pool_block: bool = False,
    ) -> None:
        self.__sock_addr = sock_addr
        super().__init__(pool_connections, pool_maxsize, max_retries, pool_block)

    def get_connection(self, url, proxies=None):
        return SocketConnectionPool(self.__sock_addr)


class Monitor:
    __socket_path = "/run/user/1001/podman/podman.sock"
    __last_read = ""

    watch_events = ["start", "die"]

    @staticmethod
    def __now_iso() -> str:
        return datetime.now(UTC).replace(microsecond=0, tzinfo=None).isoformat()

    @staticmethod
    def read(custom_socket: str | None = None) -> list[dict[str, Any]]:
        """Read events that occurred since the last time read was called.

        Currently only watches for container starts and stops. Append to
        `Monitor.watch_events` filters from podman-events(1) to add new
        functionality.

        Parameters
        ----------
        custom_socket: str, optional
            Custom Podman socket path (default is "/run/user/1001/podman/podman.sock")

        Returns
        -------
        list[dict[str, Any]]
            filtered events received from Podman
        """
        if custom_socket:
            socket_path = custom_socket
        else:
            socket_path = Monitor.__socket_path

        if Monitor.__last_read == "":
            Monitor.__last_read = Monitor.__now_iso()

        session = requests.Session()
        session.mount("http://localhost/", SocketAdapter(socket_path))
        response = session.get(
            f"http://localhost/events?since={Monitor.__last_read}&stream=false"
        )
        response.raise_for_status()

        events = []
        for entry in response.content.decode("utf-8").split("\n"):
            if len(entry) > 0:
                events.append(json.loads(entry))

        events = list(filter(lambda e: e["status"] in Monitor.watch_events, events))
        Monitor.__last_read = Monitor.__now_iso()
        return events
