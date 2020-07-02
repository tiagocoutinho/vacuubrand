import logging


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
    # ignore 'last serial command incorrect' because it seems
    # to be always active
    text = text[:-1]
    return [error for i, error in zip(text, ERRORS) if i == '1']


def decode_interval(text):
    minutes, seconds = [int(v) for v in text[:4].split(':')]
    return minutes*60 + seconds


def serial_for_url(url, *args, **kwargs):
    import serial
    conn = serial.serial_for_url(url, *args, **kwargs)
    def write_readline(data):
        conn.write(data)
        return conn.readline()
    conn.write_readline = write_readline
    return conn


class DCP3000:

    def __init__(self, connection):
        """
        Args:
            connection (object): any object with write_readline method.
                Typical are sockio.TCP or serialio.aio.tcp.Serial
        """
        self._log = logging.getLogger('vacuubrand.DCP300')
        self._conn = connection

    def _ask(self, request):
        request = (request + '\r\n').encode()
        self._log.debug('request: %r', request)
        reply = self._conn.write_readline(request)
        self._log.debug('reply: %r', reply)
        return reply.decode().strip()

    def _send(self, request):
        request = (request + '\r\n').encode()
        reply = self._conn.write(request)

    @property
    def config(self):
        return decode_config(self._ask('IN_CFG'))

    @property
    def actual_pressure(self):
        return decode_pressure(self._ask('IN_PV_1'))

    def read_transducer_pressure(self, channel=1):
        return decode_pressure(self._ask('IN_PV_S{}'.format(channel)))

    @property
    def transducer_pressures(self):
        return decode_pressures(self._ask('IN_PV_X'))

    @property
    def event_time_interval(self):
        return decode_interval(self._ask('IN_SP_1'))

    @event_time_interval.setter
    def event_time_interval(self, event_time_interval):
        self._send('OUT_SP_1 {}'.format(event_time_interval))

    @property
    def recording_time_interval(self):
        return decode_interval(self._ask('IN_SP_2'))

    @recording_time_interval.setter
    def recording_time_interval(self, recording_time_interval):
        self._send('OUT_SP_2 {}'.format(recording_time_interval))

    @property
    def errors(self):
        return decode_errors(self._ask('IN_ERR'))

    @property
    def software_version(self):
        return self._ask('IN_VER')

    def remote(self, on_off):
        self._send('REMOTE {}'.format('1' if on_off else '-'))

    def venting(self, valve):
        # valve closed(0), valve open(1), until atm. pressure(2)
        assert valve in (0, 1, 2)
        self._send('OUT_VENT {}'.format(valve))
