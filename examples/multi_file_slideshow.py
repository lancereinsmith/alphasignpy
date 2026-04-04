"""Configure multiple TEXT files and a run sequence for an automatic slideshow.

The sign cycles through three messages automatically using the run sequence.
"""

import time

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteSpecialFunction, WriteText
from alphasign.protocol import Color, DisplayMode, FileType
from alphasign.text_format import color

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)


def send(cmd):
    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(cmd)
    sign.send(pkt)
    time.sleep(0.5)


# Allocate three TEXT files.
send(
    WriteSpecialFunction.configure_memory(
        [
            {"label": "A", "type": FileType.TEXT, "size": 128},
            {"label": "B", "type": FileType.TEXT, "size": 128},
            {"label": "C", "type": FileType.TEXT, "size": 128},
        ]
    )
)
time.sleep(1)

# Write a different message into each file with a different transition.
send(
    WriteText(
        color(Color.RED) + b"WELCOME",
        label="A",
        mode=DisplayMode.ROLL_IN,
    )
)
send(
    WriteText(
        color(Color.GREEN) + b"alphasignpy demo",
        label="B",
        mode=DisplayMode.WIPE_IN,
    )
)
send(
    WriteText(
        color(Color.YELLOW) + b"Have a great day!",
        label="C",
        mode=DisplayMode.EXPLODE,
    )
)

# Tell the sign to play them in order: A -> B -> C.
send(WriteSpecialFunction.set_run_sequence("ABC"))

sign.close()
print("Slideshow running -- press RESET on the sign to stop.")
