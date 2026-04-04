"""Simplest possible example -- send a message to the sign."""

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteText
from alphasign.protocol import DisplayMode

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)

# Priority file "0" always exists -- no memory configuration needed.
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(b"Hello, World!", label="0", mode=DisplayMode.HOLD))
sign.send(pkt)

sign.close()
