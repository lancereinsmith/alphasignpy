"""Use STRING variables for live-updating content without resending the layout.

STRING files act as variables: you embed a reference in a TEXT file, then
update only the STRING contents when the data changes.  The sign redraws
automatically.
"""

import time

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteSpecialFunction, WriteString, WriteText
from alphasign.protocol import Color, DisplayMode, FileType
from alphasign.text_format import color, string_ref

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)


def send(cmd):
    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(cmd)
    sign.send(pkt)
    time.sleep(0.3)


# Allocate a TEXT file and two STRING variables.
send(
    WriteSpecialFunction.configure_memory(
        [
            {"label": "A", "type": FileType.TEXT, "size": 128},
            {"label": "a", "type": FileType.STRING, "size": 32},
            {"label": "b", "type": FileType.STRING, "size": 32},
        ]
    )
)
time.sleep(1)

# Write the TEXT layout once -- it references the two strings.
layout = (
    color(Color.AMBER)
    + b"Temp: "
    + color(Color.RED)
    + string_ref("a")
    + b"  "
    + color(Color.AMBER)
    + b"Humidity: "
    + color(Color.GREEN)
    + string_ref("b")
)
send(WriteText(layout, label="A", mode=DisplayMode.HOLD))

# Simulate sensor updates -- only the STRING data changes.
readings = [
    (b"22.5C", b"45%"),
    (b"23.1C", b"43%"),
    (b"21.8C", b"48%"),
    (b"24.0C", b"41%"),
]

for temp, humidity in readings:
    print(f"Updating: temp={temp.decode()}, humidity={humidity.decode()}")
    send(WriteString(temp, label="a"))
    send(WriteString(humidity, label="b"))
    time.sleep(3)

sign.close()
