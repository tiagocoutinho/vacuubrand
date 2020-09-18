from .dcp3000 import DCP3000


def main():
    import sys
    import logging
    from tango import GreenMode
    from tango.server import run

    args = ["Vacuubrand"] + sys.argv[1:]
    fmt = "%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)
    run((DCP3000,), args=args, green_mode=GreenMode.Asyncio)
