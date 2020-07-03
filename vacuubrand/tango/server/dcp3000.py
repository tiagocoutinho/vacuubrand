import serial
from tango import DevState
from tango.server import Device, attribute, command, device_property

from ... import dcp3000


ATTR_MAP = {
    'pressure': lambda dcp: dcp.pressure(),
    'transducer_pressure': lambda dcp: dcp.transducer_pressure(),
    'version': lambda dcp: dcp.version(),
    'errors': lambda dcp: dcp.errors(),
    'on_setpoint_1': lambda dcp: dcp.on_setpoint(1),
    'on_setpoint_2': lambda dcp: dcp.on_setpoint(2),
    'on_setpoint_3': lambda dcp: dcp.on_setpoint(3),
    'on_setpoint_4': lambda dcp: dcp.on_setpoint(4),
    'off_setpoint_1': lambda dcp: dcp.off_setpoint(1),
    'off_setpoint_2': lambda dcp: dcp.off_setpoint(2),
    'off_setpoint_3': lambda dcp: dcp.off_setpoint(3),
    'off_setpoint_4': lambda dcp: dcp.off_setpoint(4),
}

class DCP3000(Device):

    address = device_property(dtype=str)

    dcp = None

    def init_device(self):
        super().init_device()
        self.last_values = {}
        self._reconnect()

    def delete_device(self):
        super().delete_device()
        self._disconnect()

    def _try_connect(self):
        if self.dcp is None:
            try:
                conn = dcp3000.serial_for_url(self.address)
                self.dcp = dcp3000.DCP3000(conn)
            except Exception as error:
                self.connection_error = error
            else:
                self.connection_error = None

    def _disconnect(self):
        if self.dcp is not None:
            self.dcp.close()
            self.dcp = None

    def _reconnect(self):
        self._disconnect()
        self._try_connect()

    def always_executed_hook(self):
        self._try_connect()

    def _read_attr_hardware(self, indexes):
        multi_attr = self.get_device_attr()
        names = [
            multi_attr.get_attr_by_ind(index).get_name().lower()
            for index in indexes
        ]
        funcs = (ATTR_MAP[name] for name in names)
        values = [func(self.dcp) for func in funcs]
        self.last_values = dict(zip(names, values))

    def read_attr_hardware(self, indexes):
        if self.connection_error:
            raise self.connection_error
        try:
            self._read_attr_hardware(indexes)
        except Exception as error:
            self._disconnect()
            raise

    def __always_executed_hook(self):
        state, status = DevState.ON, "Ready!"
        try:
            self._connect()
            errors = self.dcp.errors()
        except Exception as error:
            state = DevState.OFF
            status = 'Communication error:\n{!r}'.format(error)
            self._disconnect()
        else:
            if errors:
                state = DevState.FAULT
                errors.insert(0, 'Hardware error(s):')
                status = '\n'.join(errors)
        self.set_state(state)
        self.set_status(status)

    def dev_state(self):
        state = DevState.ON
        if self.connection_error:
            state = DevState.OFF
        else:
            errors = self.dcp.errors()
            if errors:
                state = DevState.FAULT
        return state

    def dev_status(self):
        status = 'Ready!'
        if self.connection_error:
            status = 'Communication error:\n{!r}'.format(self.connection_error)
        else:
            errors = self.dcp.errors()
            if errors:
                status = 'Hardware error(s):\n' + '\n'.join(errors)
        self.__status = status
        return status

    @attribute(unit='mbar')
    def pressure(self):
        return self.last_values['pressure']

    @attribute(unit='mbar')
    def transducer_pressure(self):
        return self.last_values['transducer_pressure']

    @attribute(dtype=[str])
    def errors(self):
        return self.last_values['errors']

    @attribute(dtype=str)
    def version(self):
        return self.last_values['version']

    @attribute(dtype=str)
    def on_setpoint_1(self):
        return self.last_values['on_setpoint_1']

    @attribute(dtype=str)
    def on_setpoint_2(self):
        return self.last_values['on_setpoint_2']

    @attribute(dtype=str)
    def on_setpoint_3(self):
        return self.last_values['on_setpoint_3']

    @attribute(dtype=str)
    def on_setpoint_4(self):
        return self.last_values['on_setpoint_4']

    @attribute(dtype=str)
    def off_setpoint_1(self):
        return self.last_values['off_setpoint_1']

    @attribute(dtype=str)
    def off_setpoint_2(self):
        return self.last_values['off_setpoint_2']

    @attribute(dtype=str)
    def off_setpoint_3(self):
        return self.last_values['off_setpoint_3']

    @attribute(dtype=str)
    def off_setpoint_4(self):
        return self.last_values['off_setpoint_4']

    @command
    def switch_on(self):
        self.dcp.switch_on()

    @command
    def switch_off(self):
        self.dcp.switch_off()

    @command
    def open_venting_value(self):
        self.dcp.open_venting_value()

    @command
    def close_venting_valve(self):
        self.dcp.close_venting_valve()

    @command
    def vent(self):
        self.dcp.vent()


def main():
    DCP3000.run_server()


if __name__ == '__main__':
    main()
