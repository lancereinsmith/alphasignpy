"""Demonstrate special function commands: clock, memory, speaker, dimming."""

import time

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteSpecialFunction
from alphasign.protocol import DayOfWeek, FileType, TimeFormat

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)


def send(cmd):
    """Helper -- wrap a single command in a packet and send it."""
    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(cmd)
    sign.send(pkt)
    time.sleep(0.5)


# -- Set the clock ---------------------------------------------------------
print("Setting time to 14:30 (military)...")
send(WriteSpecialFunction.set_time(14, 30))

print("Setting date to March 15, 2026...")
send(WriteSpecialFunction.set_date(3, 15, 26))

print("Setting day of week to Sunday...")
send(WriteSpecialFunction.set_day_of_week(DayOfWeek.SUNDAY))

print("Setting 24-hour time format...")
send(WriteSpecialFunction.set_time_format(TimeFormat.MILITARY))

# -- Memory configuration --------------------------------------------------
print("Allocating TEXT file 'A' (256 bytes) and STRING file 'B' (64 bytes)...")
send(
    WriteSpecialFunction.configure_memory(
        [
            {"label": "A", "type": FileType.TEXT, "size": 256},
            {"label": "B", "type": FileType.STRING, "size": 64},
        ]
    )
)
time.sleep(1)

# -- Speaker and dimming ----------------------------------------------------
print("Enabling speaker...")
send(WriteSpecialFunction.set_speaker(True))

print("Playing a tone...")
send(WriteSpecialFunction.generate_tone(tone_type=2, frequency=0x80, duration=5, repeat=1))
time.sleep(1)

print("Setting brightness to 72%...")
send(WriteSpecialFunction.set_dimming_register(dim_mode=0, brightness_percent=72))

# -- Soft reset -------------------------------------------------------------
print("Sending soft reset...")
send(WriteSpecialFunction.soft_reset())

sign.close()
print("Done.")
