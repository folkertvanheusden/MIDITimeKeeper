#! /usr/bin/python3

import math
import mido
import signal
import sys
import time

# https://github.com/aewallin/allantools/
# pip3 install allantools
import allantools

import numpy as np

if len(sys.argv) == 2:
    duration = int(sys.argv) * 60

else:
    print('Program argument: time to measure in minutes. Now running forever.')
    duration = 10000000000000000000000

abort = False

def signal_handler(signum, frame):
    global abort

    signal.signal(signum, signal.SIG_IGN)

    abort = True

signal.signal(signal.SIGINT, signal_handler)

port = mido.open_input('time', virtual=True, client_name='MIDITimeKeeper')

start = time.time()

values = []

while not abort:
    msg = port.receive()
    ns = time.time_ns()

    t = ns / 1_000_000_000

    if msg.type == 'sysex' and msg.data[0] == 127 and msg.data[1] == 127 and msg.data[2] == 1 and msg.data[3] == 1:
        tm = time.localtime(int(t))

        h = msg.data[4] & 0x1f
        m = msg.data[5]
        s = msg.data[6]
        frame = msg.data[7]

        code = msg.data[4] >> 5
        mul = 0
        if code == 0:
            mul = 1 / 24.0
        elif code == 1:
            mul = 1 / 25.0
        elif code == 2:
            mul = 1 / 29.97
        elif code == 3:
            mul = 1 / 30.0

        t_rx = time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday, h, m, s, tm.tm_wday, tm.tm_yday, tm.tm_isdst))  # , tm.tm_zone, tm.tm_gmtoff
        t_rx += frame * mul

        values.append((t, t_rx))

        print(f'{time.ctime(t)}\t{time.ctime(t_rx)}\t{t - t_rx:.3f}')

    if t - start > duration:
        break

fh = open('measurements.csv', 'w')

for pair in values:
    fh.write(f'{pair[0]},{pair[1]}\n')

fh.close()

use_values = [ v[1] for v in values ]

a = allantools.Dataset(data = use_values)
a.compute("adev")

# Plot it using the Plot class
b = allantools.Plot()
# New in 2019.7 : additional keyword arguments are passed to
# matplotlib.pyplot.plot()
b.plot(a, errorbars=True, grid=True, marker='x')
# You can override defaults before "show" if needed
b.ax.set_xlabel("Tau (s)")
b.show()
