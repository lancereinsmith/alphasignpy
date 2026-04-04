"""Display a live clock with the current date on the sign."""

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteText
from alphasign.protocol import Color, DisplayMode, Font
from alphasign.text_format import CTRL_NEW_LINE, CTRL_TIME, color, date_code, font

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)

# The sign's internal clock renders the time and date live.
message = (
    font(Font.SEVEN_HIGH_STD)
    + color(Color.GREEN)
    + CTRL_TIME
    + CTRL_NEW_LINE
    + color(Color.RED)
    + date_code("mm/dd/yy")
)

pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(message, label="0", mode=DisplayMode.HOLD))
sign.send(pkt)

sign.close()
