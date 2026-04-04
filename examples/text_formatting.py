"""Demonstrate text formatting: colors, fonts, speed, flashing, and wide text."""

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteSpecialFunction, WriteText
from alphasign.protocol import Color, DisplayMode, FileType, Font
from alphasign.text_format import (
    CTRL_FLASH_OFF,
    CTRL_FLASH_ON,
    CTRL_NEW_LINE,
    CTRL_WIDE_OFF,
    CTRL_WIDE_ON,
    color,
    font,
    speed,
)

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)

# Allocate a 512-byte TEXT file at label "A".
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(
    WriteSpecialFunction.configure_memory(
        [
            {"label": "A", "type": FileType.TEXT, "size": 512},
        ]
    )
)
sign.send(pkt)

# Build a message showcasing multiple formatting features.
message = (
    # Big, slow, red header
    font(Font.SEVEN_HIGH_STD)
    + speed(1)
    + color(Color.RED)
    + b"ALERT "
    # Flashing amber warning
    + color(Color.AMBER)
    + CTRL_FLASH_ON
    + b"!!!"
    + CTRL_FLASH_OFF
    # New line -- green body text
    + CTRL_NEW_LINE
    + font(Font.FIVE_HIGH_STD)
    + speed(3)
    + color(Color.GREEN)
    + b"System nominal"
    # Wide yellow footer
    + CTRL_NEW_LINE
    + CTRL_WIDE_ON
    + color(Color.YELLOW)
    + b"OK"
    + CTRL_WIDE_OFF
)

pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(message, label="A", mode=DisplayMode.SCROLL))
sign.send(pkt)

sign.close()
