# Vacuubrand library

<img align="right" alt="DCP3000 pirani" width="350"
     src="https://github.com/tiagocoutinho/vacuubrand/raw/master/docs/dcp_3000_pirani.png" />

This library is used to control basic features of a Vacuubrand controller.

It is composed of a core library, an optional simulator and
an optional [tango](https://tango-controls.org/) device server.

So far only the DCP 3000 is supported.

## Installation

From within your favorite python environment type:

`$ pip install vacuubrand`


## Library

The core of the vacuubrand library consists of DCP3000 object.
To create a DCP3000 object you need to pass a communication object.

The communication object can be any object that supports a simple API
consisting of two methods (either the sync or async version is supported):

* `write_readline(buff: bytes) -> bytes` *or*
* `write(buff: bytes) -> None` *or*

Usually you end up using a `connio.connection_for_url()` object.
Here is how to connect to a DCP 3000 controller:

```python
import asyncio
from connio import connection_for_url
from vacuubrand.dcp3000 import DCP3000


async def main():
    # could also be a socket bridge: 'serial-tcp://<host>:<port>'
    comm = connection_for_url('serial:///dev/ttyS0')
    dcp = DCP3000(comm)

    print(await dcp.pressure())


asyncio.run(main())
```

#### Serial line

To access a serial line based DCP 3000 device it is strongly recommended you spawn
a serial to tcp bridge using [ser2net](https://linux.die.net/man/8/ser2net) or
[socat](https://linux.die.net/man/1/socat)

Assuming your device is connected to `/dev/ttyS0` and the baudrate is set to 19200,
here is how you could use socat to expose your device on the machine port 5000:

`socat -v TCP-LISTEN:8500,reuseaddr,fork file:/dev/ttyS0,rawer,b19200,cs8,eol=10,icanon=1`

The equivalent line in ser2net config file would be:
```
8500:raw:0:/dev/ttyR15:19200 8DATABITS NONE 1STOPBIT
```

It might be worth considering starting socat or ser2net as a service using
[supervisor](http://supervisord.org/) or [circus](https://circus.rtfd.io/).

### Simulator

A DCP 3000 simulator is provided.

Before using it, make sure everything is installed with:

`$ pip install vacuubrand[simulator]`

The [sinstruments](https://pypi.org/project/sinstruments/) engine is used.

To start a simulator you need to write a YAML config file where you define
how many devices you want to simulate and which properties they hold.

The following example exports 2 hardware devices. The first is a minimal
configuration using default values and the second defines some initial values
explicitly:

```yaml
# config.yml

devices:
- class: DCP3000
  package: vacuubrand.simulator
  transports:
  - type: serial
    url: /tmp/dcp3000-1

```

To start the simulator type:

```terminal
$ sinstruments-server -c ./config.yml --log-level=DEBUG
2020-07-02 12:18:45,065 INFO  simulator: Bootstraping server
2020-07-02 12:18:45,065 INFO  simulator: no backdoor declared
2020-07-02 12:18:45,065 INFO  simulator: Creating device DCP3000 ('DCP3000')
2020-07-02 12:18:45,067 INFO  simulator: Created symbolic link "/tmp/dcp3000-1" to simulator pseudo terminal '/dev/pts/7'
2020-07-02 12:18:45,067 INFO  simulator.DCP3000[/tmp/dcp3000-1]: listening on /tmp/dcp3000-1 (baud=None)
```

(To see the full list of options type `sinstruments-server --help`)

You can access it as you would a real hardware:

```terminal
$ miniterm.py -e --eol CRLF /tmp/dcp3000-1
IN_PV_1
1004.1 mbar
```

or using the library:
```python
$ python
>>> from connio import connection_for_url
>>> from vacuubrand.dcp3000 import DCP3000
>>> conn = connection_for_url("serial:///tmp/dcp3000-1")
>>> dcp = DCP3000(conn)
>>> print(await dcp.actual_pressure())
1004.1
```

### Tango server

A [tango](https://tango-controls.org/) device server is also provided.

Make sure everything is installed with:

`$ pip install vacuubrand[tango]`

Register a Vacuubrand tango server in the tango database:
```
$ tangoctl server add -s Vacuubrand/test -d DCP3000 test/dcp3000/1
$ tangoctl device property write -d test/dcp3000/1 -p url -v "/dev/ttyS0"
```

(the above example uses [tangoctl](https://pypi.org/project/tangoctl/). You would need
to install it with `pip install tangoctl` before using it. You are free to use any other
tango tool like [fandango](https://pypi.org/project/fandango/) or Jive)

Launch the server with:

```terminal
$ Vacuubrand test
```

