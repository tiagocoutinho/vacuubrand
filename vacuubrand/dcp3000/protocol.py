import enum
import time
import asyncio
import logging
import functools
import threading

from connio import connection_for_url


UNITS = {"0": "mbar", "1": "Torr", "2": "hPa"}


ERRORS = [
    "venting valve fault",
    "overpressure",
    "pressure transducer fault",
    "external fault",
    #    'last serial command incorrect'
]


torr_to_mbar = 1.3332236842105263


def syncer(func):
    async def acall(coro):
        return func(await coro)

    @functools.wraps(func)
    def wrapper(arg):
        return acall(arg) if asyncio.iscoroutine(arg) else func(arg)

    return wrapper


@syncer
def decode_config(text):
    assert len(text) == 7, text
    return dict(
        unit=UNITS[text[1]],
        acoustic_signal=text[2] == "1",
        venting_valve_connected=text[3] == "1",
        fault_indicator_connected=text[4] == "1",
        nb_active_pressure_transducers=int(text[5]),
        nb_pressure_transducers=int(text[6]),
    )


@syncer
def decode_pressure(text):
    value, unit = text.lower().split()
    value = float(value)
    if unit == "torr":
        value *= torr_to_mbar
    return value


@syncer
def decode_pressures(text):
    """decode pressure(s). Always return values in millibar"""
    *values, unit = text.lower().split()
    values = [float(value) for value in values]
    if unit == "torr":
        values = [value * torr_to_mbar for value in values]
    return values


@syncer
def decode_errors(text):
    """return a list of errors"""
    assert len(text) == 5, text
    text = text[:-1]
    return [error for i, error in zip(text, ERRORS) if i == "1"]


@syncer
def decode_interval(text):
    minutes, seconds = [int(v) for v in text[:4].split(":")]
    return minutes * 60 + seconds


def encode(request):
    return request.encode() + b"\n"


def decode(reply):
    return reply.decode().strip()


class BaseProtocol:
    """
    Handles communication protocol
    - latency / back-pressure
    - encode/decode bytes <-> text
    - serializes read calls
    """

    # max 20 commands/s (according to doc) <=> 50 ms (put 60 to be safe side)
    COMMAND_LATENCY = 0.06

    def __init__(self, connection, log=None):
        self.conn = connection
        self._last_command = 0
        self._log = log or logging.getLogger(
            "vacuubrand.dcp3000.{}".format(type(self).__name__)
        )

    def _wait_time(self):
        return self._last_command + self.COMMAND_LATENCY - time.monotonic()


class AIOProtocol(BaseProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = asyncio.Lock()

    async def _back_pressure(self):
        wait = self._wait_time()
        if wait > 0:
            await asyncio.sleep(wait)

    async def write_readline(self, data):  # aka: query or put_get
        data = encode(data)
        self._log.debug("write: %r", data)
        await self._back_pressure()
        try:
            async with self._lock:
                # TODO: maybe consume garbage in the buffer ?
                reply = await self.conn.write_readline(data)
            self._log.debug("read: %r", reply)
            return decode(reply)
        finally:
            self._last_command = time.monotonic()

    async def write(self, data):
        data = encode(data)
        self._log.debug("write: %r", data)
        await self._back_pressure()
        try:
            await self.conn.write(data)
        finally:
            self._last_command = time.monotonic()


class IOProtocol(BaseProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()

    def _back_pressure(self):
        wait = self._wait_time()
        if wait > 0:
            time.sleep(wait)

    def write_readline(self, data):  # aka: query or put_get
        data = encode(data)
        self._log.debug("write: %r", data)
        self._back_pressure()
        try:
            with self._lock:
                # TODO: maybe consume garbage in the buffer ?
                reply = self.conn.write_readline(data)
            self._log.debug("read: %r", reply)
            return decode(reply)
        finally:
            self._last_command = time.monotonic()

    def write(self, data):  # aka: query or put_get
        data = encode(data)
        self._log.debug("write: %r", data)
        self._back_pressure()
        try:
            self.conn.write(data)
        finally:
            self._last_command = time.monotonic()


def Protocol(connection, *args, **kwargs):
    func = connection.write_readline
    klass = AIOProtocol if asyncio.iscoroutinefunction(func) else IOProtocol
    return klass(connection, *args, **kwargs)


def protocol_for_url(url, *args, **kwargs):
    log = kwargs.pop("log", None)
    conn = connection_for_url(url, *args, **kwargs)
    return Protocol(conn, log=log)
