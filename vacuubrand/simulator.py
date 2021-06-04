# -*- coding: utf-8 -*-
#
# This file is part of the vacuubrand project
#
# Copyright (c) 2020 Tiago Coutinho
# Distributed under the LGPLv3. See LICENSE for more info.

"""
.. code-block:: yaml

    devices:
    - class: DCP3000
      name: vacuubrand-1
      transports:
      - type: serial
        url: /tmp/dcp3000-1
"""

from sinstruments.simulator import BaseDevice


DEFAULT = {
    "IN_VER": "DCP 3000  V2.30",
    "IN_PV_S1": "0234 mbar",
    "IN_PV_S2": "0278 mbar",
    "IN_PV_S3": "0213 mbar",
    "IN_PV_S4": "0223 mbar",
    "IN_PV_X": "0362 0234 0278 0213 mbar",
    # English, mbar, no acoustic signal, venting valve, fault indicator, 4 transducers
    "IN_CFG": "1001144",
    "IN_ERR": "00000",
    "IN_SP_1": "00:00",  # time interval for sending
    "IN_SP_2": "99:00",  # time interval for recording
    "IN_SP_11": "111.0 mbar",  # On setpoint channel 1
    "IN_SP_21": "011.5 mbar",  # Off setpoint channel 1
    "IN_SP_12": "222.0 mbar",  # On setpoint channel 1
    "IN_SP_22": "022.5 mbar",  # Off setpoint channel 1
    "IN_SP_13": "333.0 mbar",  # On setpoint channel 1
    "IN_SP_23": "033.5 mbar",  # Off setpoint channel 1
    "IN_SP_14": "444.0 mbar",  # On setpoint channel 1
    "IN_SP_24": "044.5 mbar",  # Off setpoint channel 1
}


def to_hh_ss(text):
    if ":" in text:
        return text
    sec = int(text)
    return "{:02d}:{:02d}".format(sec // 60, sec % 60)


class DCP3000(BaseDevice):
    def __init__(self, name, **opts):
        kwargs = {}
        if "newline" in opts:
            kwargs["newline"] = opts.pop("newline")
        self._config = dict(DEFAULT, **opts)
        self._on = True
        super().__init__(name, **kwargs)

    def handle_message(self, line):
        self._log.debug("request %r", line)
        line = line.decode().strip()
        result = None
        cmd, *args = line.split(" ", 1)
        if cmd == "OUT_SP_1":
            self._config["IN_SP_1"] = to_hh_ss(args[0])
        elif line.startswith("OUT_SP_2"):
            self._config["IN_SP_2"] = to_hh_ss(args[0])
        elif cmd == "OUT_VENT":
            pass
        elif cmd == "OUT_SENSOR":
            pass
        elif cmd == "REMOTE":
            self._on = args[0] == "1"
        elif cmd.startswith("OUT_SP_"):
            self._config["IN_SP_" + cmd[7:9]] = args[0]
        elif line == "IN_PV_1":
            v = "1004.1" if self._on else "0000.0"
            result = v + " mbar"
        else:
            result = self._config.get(line)
        if result is None:
            return
        result = result.encode() + b"\r\n"
        self._log.debug("reply %r", result)
        return result
