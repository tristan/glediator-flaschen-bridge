
# Glediator to Flashen Taschen Bridge

Bridges the serial output of [Glediator](http://www.solderlab.de/index.php/software/glediator)
To a [Flaschen Taschen](https://github.com/hzeller/flaschen-taschen) Server

# Install

```
virtualenv env
env/bin/pip install pyserial
```

# Usage

```
env/bin/python glediator_flaschen_bridge.py <flaschen-taschen-ip-address> <screen-width>x<screen-height> <layer (default=0)>
```

This will print out the name of the tty (e.g. `/dev/ttys006`) it creates, then run Glediator with (replacing X with the tty number):

```
java -Dgnu.io.rxtx.SerialPorts=/dev/ttys00X -jar Glediator_V2.jar
```

e.g.

```
$ env/bin/python glediator_flaschen_bridge.py 192.168.1.141 48x36
Created serial port: /dev/ttys006

$ java -Dgnu.io.rxtx.SerialPorts=/dev/ttys006 -jar Glediator_V2.jar
```
