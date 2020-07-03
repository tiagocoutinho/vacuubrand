import time
import logging
import threading


# max 20 commands/s (according to doc) <=> 50 ms (put 60 to be safe side)
SERIAL_LATENCY = 0.06

UNITS = {
    '0': 'mbar',
    '1': 'Torr',
    '2': 'hPa'
}


ERRORS = [
    'venting valve fault',
    'overpressure',
    'pressure transducer fault',
    'external fault',
#    'last serial command incorrect'
]


torr_to_mbar = 1.3332236842105263


def decode_config(text):
    assert len(text) == 7, text
    return dict(unit=UNITS[text[1]],
                acoustic_signal=text[2] == '1',
                venting_valve_connected=text[3] == '1',
                fault_indicator_connected=text[4] == '1',
                nb_active_pressure_transducers=int(text[5]),
                nb_pressure_transducers=int(text[6]))


def decode_pressure(text):
    value, unit = text.lower().split()
    value = float(value)
    if unit == 'torr':
        value *= torr_to_mbar
    return value


def decode_pressures(text):
    """decode pressure(s). Always return values in millibar"""
    *values, unit = text.lower().split()
    values = [float(value) for value in values]
    if unit == 'torr':
        values = [value * torr_to_mbar for value in values]
    return values


def decode_errors(text):
    """return a list of errors"""
    assert len(text) == 5, text
    text = text[:-1]
    return [error for i, error in zip(text, ERRORS) if i == '1']


def decode_interval(text):
    minutes, seconds = [int(v) for v in text[:4].split(':')]
    return minutes*60 + seconds


def serial_for_url(url, *args, **kwargs):
    import serial
    opts = dict(
        baudrate=19200, bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
        xonxoff=False, rtscts=False, timeout=1
    )
    opts.update(kwargs)
    conn = serial.serial_for_url(url, *args, **opts)
    lock = threading.Lock()
    conn._last_comm = 0

    def back_pressure():
        now = time.monotonic()
        wait = SERIAL_LATENCY - now + conn._last_comm
        if wait > 0:
            time.sleep(wait)

    def consume():
        data = []
        while(conn.in_waiting):
            data.append(conn.read(conn.in_waiting))
        return b''.join(data)

    def send(data):
        back_pressure()
        try:
            conn.write(data)
        finally:
            self._last_comm = time.monotonic()

    def write_readline(data):
        back_pressure()
        try:
            with lock:
                garbage = conn.consume()
                if garbage:
                    logging.warning('disposed of %r', garbage)
                conn.write(data)
                return conn.readline()
        finally:
            conn._last_comm = time.monotonic()
    conn.consume = consume
    conn.send = send
    conn.write_readline = write_readline
    return conn


class DCP3000:

    latency = 0.06

    def __init__(self, connection):
        """
        Args:
            connection (object): any object with write_readline method.
                Typical are sockio.TCP or serialio.aio.tcp.Serial
        """
        self._log = logging.getLogger('vacuubrand.DCP300')
        self._conn = connection

    def close(self):
        self._conn.close()

    def _ask(self, request):
        request = (request + '\n').encode()
        self._log.debug('request: %r', request)
        reply = self._conn.write_readline(request)
        self._log.debug('reply: %r', reply)
        return reply.decode().strip()

    def _send(self, request):
        request = (request + '\n').encode()
        self._log.debug('command: %r', request)
        self._conn.write(request)

    def config(self):
        return decode_config(self._ask('IN_CFG'))

    def pressure(self):
        return decode_pressure(self._ask('IN_PV_1'))

    def transducer_pressure(self, channel=1):
        return decode_pressure(self._ask('IN_PV_S{}'.format(channel)))

    def transducer_pressures(self):
        return decode_pressures(self._ask('IN_PV_X'))

    def event_time_interval(self, value: int = None):
        if value is not None:
            self._send('OUT_SP_1 {}'.format(value))
        return decode_interval(self._ask('IN_SP_1'))

    def recording_time_interval(self, value: int = None):
        if value is not None:
            self._send('OUT_SP_2 {}'.format(value))
        return decode_interval(self._ask('IN_SP_2'))

    def _set_point(self, channel: int, on_off: bool, value: (float, 'mbar') = None):
        assert channel in {1, 2, 3, 4}
        on_off = 1 if on_off else 2
        if value is not None:
            self._send('OUT_SP_{}{} {} mbar'.format(on_off, channel, value))
        return self._ask('IN_SP_{}{}'.format(on_off, channel))

    def on_setpoint(self, channel: int, value: (float, 'mbar') = None):
        return self._set_point(channel, True, value=value)

    def off_setpoint(self, channel: int, value: (float, 'mbar') = None):
        return self._set_point(channel, False, value=value)

    def errors(self):
        return decode_errors(self._ask('IN_ERR'))

    def version(self):
        return self._ask('IN_VER')

    def switch_on(self):
        self._send('REMOTE 1')

    def switch_off(self):
        self._send('REMOTE -')

    def close_venting_valve(self):
        self._send('OUT_VENT 0')

    def open_venting_value(self):
        self._send('OUT_VENT 1')

    def vent(self):
        """venting until atmospheric pressure"""
        self._send('OUT_VENT 2')
