# bridge for Glediator serial output to flaschen taschen server
# NOTE:
# run glediator with the following to access the ttys00X (replacing X with the tty number)
#     java -Dgnu.io.rxtx.SerialPorts=/dev/ttys00X -jar Glediator_V2.jar

import os, pty, serial, sys, socket

class Flaschen(object):
    '''A Framebuffer display interface that sends a frame via UDP.'''

    def __init__(self, host, port, width, height, layer=0, transparent=False):
        '''
        Args:
          host: The flaschen taschen server hostname or ip address.
          port: The flaschen taschen server port number.
          width: The width of the flaschen taschen display in pixels.
          height: The height of the flaschen taschen display in pixels.
          layer: The layer of the flaschen taschen display to write to.
          transparent: If true, black(0, 0, 0) will be transparent and show the layer below.
        '''
        self.width = width
        self.height = height
        self.layer = layer
        self.transparent = transparent
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.connect((host, port))
        header = ''.join(["P6\n",
                          "%d %d\n" % (self.width, self.height),
                          "255\n"])
        footer = ''.join(["0\n",
                          "0\n",
                          "%d\n" % self.layer])
        self._data = bytearray(width * height * 3 + len(header) + len(footer))
        self._data[0:len(header)] = header
        self._data[-1 * len(footer):] = footer
        self._header_len = len(header)

    def set(self, x, y, color):
        '''Set the pixel at the given coordinates to the specified color.
        Args:
          x: x offset of the pixel to set
          y: y offset of the piyel to set
          color: A 3 tuple of (r, g, b) color values, 0-255
        '''
        if x >= self.width or y >= self.height or x < 0 or y < 0:
            return
        if color == (0, 0, 0) and not self.transparent:
            color = (1, 1, 1)

        offset = (x + y * self.width) * 3 + self._header_len
        self._data[offset] = color[0]
        self._data[offset + 1] = color[1]
        self._data[offset + 2] = color[2]

    def send(self):
        '''Send the updated pixels to the display.'''
        self._sock.send(self._data)

if __name__ == '__main__':

    if len(sys.argv) < 3 or 'x' not in sys.argv[2]:
        print "Missing or invalid arguments:"
        print "    %s [flashen-ip-address] [width]x[height] [layer]"
        sys.exit(1)

    faddr = sys.argv[1]
    w, h = sys.argv[2].split('x')
    w = int(w)
    h = int(h)
    layer = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    master, slave = pty.openpty()
    s_name = os.ttyname(slave)

    print 'Created serial port: %s' % s_name

    ser = serial.Serial(s_name, 9600, rtscts=True, dsrdtr=True)

    # connect to flashen
    flaschen = Flaschen(faddr, 1337, w, h, layer)

    # main loop
    no_pixels = w * h
    pixelno = 0
    x = 0
    y = 0
    STATE_RED = 0
    STATE_GREEN = 1
    STATE_BLUE = 2
    state = STATE_RED
    currentcolour = [0, 0, 0]
    has_sent = True
    has_started = False
    while True:
        data = os.read(master, 1000)

        for i in data:
            if ord(i) == 1:
                if not has_started:
                    print "STARTING!!!"
                    has_started = True
                if not has_sent:
                    print "WARNING: incomplete frame!!!"
                state = STATE_RED
                pixelno = 0
                x = 0
                y = 0
                has_sent = False
            else:
                if not has_started:
                    continue
                if has_sent:
                    print "WARNING: frame already sent!!!"
                if state == STATE_RED:
                    currentcolour[0] = ord(i)
                    state = STATE_GREEN
                elif state == STATE_GREEN:
                    currentcolour[1] = ord(i)
                    state = STATE_BLUE
                elif state == STATE_BLUE:
                    currentcolour[2] = ord(i)

                    flaschen.set(x, y, currentcolour)

                    # update new pixel
                    x = (x + 1) % w
                    if x == 0:
                        y = (y + 1) % h
                        if y == 0:
                            # this is the last pixel
                            flaschen.send()
                            has_sent = True

                    state = STATE_RED
