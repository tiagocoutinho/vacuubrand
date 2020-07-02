from .dcp3000 import DCP3000


def main():
    import sys
    import logging
    from tango.server import run
    args = ['Vacuubrand'] + sys.argv[1:]
    logging.basicConfig(level="DEBUG")
    run((DCP3000,), args=args)
