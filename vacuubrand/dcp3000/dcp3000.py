import logging

from .protocol import (
    Protocol,
    decode_config,
    decode_pressure,
    decode_pressures,
    decode_interval,
    decode_errors,
)


class DCP3000:
    def __init__(self, connection):
        self._log = logging.getLogger("xia_pfcu.{}".format(type(self).__name__))
        self.protocol = Protocol(connection, log=self._log)

    def write_readline(self, request):
        return self.protocol.write_readline(request)

    def write(self, request):
        return self.protocol.write(request)

    def config(self):
        reply = self.write_readline("IN_CFG")
        return decode_config(reply)

    def pressure(self):
        reply = self.write_readline("IN_PV_1")
        return decode_pressure(reply)

    def transducer_pressure(self, channel=1):
        reply = self.write_readline("IN_PV_S{}".format(channel))
        return decode_pressure(reply)

    def transducer_pressures(self):
        reply = self.write_readline("IN_PV_X")
        return decode_pressures(reply)

    def event_time_interval(self, value: int = None):
        if value is not None:
            return self.write("OUT_SP_1 {}".format(value))
        reply = self.write_readline("IN_SP_1")
        return decode_interval(reply)

    def recording_time_interval(self, value: int = None):
        if value is not None:
            self.write("OUT_SP_2 {}".format(value))
        reply = self.write_readline("IN_SP_2")
        return decode_interval(reply)

    def _set_point(self, channel: int, on_off: bool, value: (float, "mbar") = None):
        assert channel in {1, 2, 3, 4}
        on_off = 1 if on_off else 2
        if value is not None:
            return self.write("OUT_SP_{}{} {} mbar".format(on_off, channel, value))
        reply = self.write_readline("IN_SP_{}{}".format(on_off, channel))
        return decode_pressure(reply)

    def on_setpoint(self, channel: int, value: (float, "mbar") = None):
        return self._set_point(channel, True, value=value)

    def off_setpoint(self, channel: int, value: (float, "mbar") = None):
        return self._set_point(channel, False, value=value)

    def errors(self):
        reply = self.write_readline("IN_ERR")
        return decode_errors(reply)

    def version(self):
        return self.write_readline("IN_VER")

    def switch_on(self):
        return self.write("REMOTE 1")

    def switch_off(self):
        return self.write("REMOTE -")

    def close_venting_valve(self):
        return self.write("OUT_VENT 0")

    def open_venting_value(self):
        return self.write("OUT_VENT 1")

    def vent(self):
        """venting until atmospheric pressure"""
        return self.write("OUT_VENT 2")
