import urllib.parse

from tango import DevState, GreenMode
from tango.server import Device, attribute, command, device_property
from connio import connection_for_url

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

    green_mode = GreenMode.Asyncio

    url = device_property(dtype=str)
    baudrate = device_property(dtype=int, default_value=9600)
    bytesize = device_property(dtype=int, default_value=8)
    parity = device_property(dtype=str, default_value="N")

    dcp = None

    def url_to_connection_args(self):
        url = self.url
        res = urllib.parse.urlparse(url)
        kwargs = dict(concurrency="async")
        if res.scheme in {"serial", "rfc2217"}:
            kwargs.update(dict(baudrate=self.baudrate, bytesize=self.bytesize,
                               parity=self.parity))
        return url, kwargs

    async def init_device(self):
        await super().init_device()
        url, kwargs = self.url_to_connection_args()
        conn = connection_for_url(url, **kwargs)
        self.dcp = dcp3000.DCP3000(conn)
        self.last_values = {}

    async def read_attr_hardware(self, indexes):
        multi_attr = self.get_device_attr()
        names = [
            multi_attr.get_attr_by_ind(index).get_name().lower()
            for index in indexes
        ]
        funcs = (ATTR_MAP[name] for name in names)
        values = [await func(self.dcp) for func in funcs]
        self.last_values = dict(zip(names, values))

    async def dev_state(self):
        state = DevState.ON
        try:
            errors = await self.dcp.errors()
            if errors:
                state = DevState.ALARM
        except:
            state = DevState.FAULT
        return state

    async def dev_status(self):
        self.__status = 'Ready!'
        try:
            errors = await self.dcp.errors()
            if errors:
                self.__status = 'Hardware error(s):\n' + '\n'.join(errors)
        except Exception as error:
            self.__status = 'Communication error:\n{!r}'.format(error)
        return self.__status

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
