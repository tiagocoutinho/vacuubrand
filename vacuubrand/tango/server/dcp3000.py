from tango.server import Device, attribute, command, device_property

from ... import dcp3000


class DCP3000(Device):

    address = device_property(dtype=str)

    def init_device(self):
        super().init_device()
        conn = dcp3000.serial_for_url(self.address)
        self.dcp = dcp3000.DCP3000(conn)

    @attribute(unit='mbar')
    def pressure(self):
        return self.dcp.pressure()

    @attribute(unit='mbar')
    def transducer_pressure(self):
        return self.dcp.transducer_pressure()

    @attribute(dtype=[str])
    def errors(self):
        return self.dcp.errors()

    @attribute(dtype=str)
    def software_version(self):
        return self.dcp.software_version()

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

