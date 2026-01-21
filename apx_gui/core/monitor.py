# apx.py
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

import json
import os
import podman
import logging

from typing import Any

from datetime import datetime, UTC
from podman import PodmanClient

logger = logging.getLogger(__name__)

class Monitor:
    __last_read = datetime.now(UTC)
    runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
    if not runtime_dir:
        runtime_dir = f"/run/user/{os.getuid()}"
    __socket_path = f"{runtime_dir}/podman/podman.sock"

    watch_events = ["event=start", "event=died"]

    @staticmethod
    def read(custom_socket: str | None = None) -> list[dict[str, Any]]:
        """Read events that occurred since the last time read was called.

        Currently only watches for container starts and stops. Append to
        `Monitor.watch_events` filters from podman-events(1) to add new
        functionality.

        Returns
        -------
        list[dict[str, Any]]
            filtered events received from Podman
        """
        if custom_socket:
            podman_uri = f"unix://{custom_socket}"
        else:
            podman_uri = f"unix://{Monitor.__socket_path}"

        now = datetime.now(UTC)

        try:
            with PodmanClient(base_url=podman_uri) as client:
                events = client.events(
                    since = Monitor.__last_read,
                    until = now,
                    filters = Monitor.watch_events,
                    decode = True
                )
                client.close()

                events_list = list(events)
                if len(events_list) > 0:
                    logger.debug(f"DEBUG: SUCCESS! Found {len(events_list)} events.")
                    for e in events_list:
                        logger.debug(f"  - Event: {e.get('Action')} | Type: {e.get('Type')} | Status: {e.get('status')}")
                else:
                    logger.debug("DEBUG: Window was empty. Try starting/stopping a container now.")

                Monitor.__last_read = now
                return events_list

        except Exception as err:
            logger.error(f"Unexpected error: {err}")
            return
