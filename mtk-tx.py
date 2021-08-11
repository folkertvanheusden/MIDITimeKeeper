#! /usr/bin/python3

import mido
import time

port = mido.open_output('time', virtual=True, client_name='MIDITimeKeeper')

pframe = None

while True:
    ns = time.time_ns()

    ms = (ns // 1_000_000) % 1000
    frame = ms // 40

    if frame != pframe:
        pframe = frame

        t = ns // 1_000_000_000
        tm = time.localtime(t)

        h = tm.tm_hour
        m = tm.tm_min
        s = tm.tm_sec

        msg = ( 0x7f, 0x7f, 0x01, 0x01, 0x60 | h, m, s, frame )  # MIDO adds 0xf0 ... 0xf7

        port.send(mido.Message('sysex', data=msg, time=0))

    time.sleep(1/50.0)
