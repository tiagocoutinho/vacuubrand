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
      package: vacuubrand.simulator
      transports:
      - type: serial
        url: /tmp/dcp3000-1
"""

import time

from sinstruments.simulator import BaseDevice


DEFAULT = {
    'IN_PV_1': '1004.1 mbar',
}


class DCP3000(BaseDevice):


    def __init__(self, name, **opts):
        kwargs = {}
        if 'newline' in opts:
            kwargs['newline'] = opts.pop('newline')
        self._config = dict(DEFAULT, **opts)
        super().__init__(name, **kwargs)

    def handle_message(self, line):
        self._log.debug('request %r', line)
        line = line.decode().strip()
        return self._config[line].encode() + b'\r\n'

