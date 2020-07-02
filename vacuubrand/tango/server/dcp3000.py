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



def main():
    import sys
    import logging
    from tango.server import run
    args = ['Vacuubrand'] + sys.argv[1:]
    logging.basicConfig(level="DEBUG")
    run((DCP3000,), args=args)


if __name__ == '__main__':
    main()
        
