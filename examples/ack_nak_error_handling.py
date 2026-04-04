"""Demonstrate ACK/NAK error checking for reliable communication.

Alpha 2.0+ signs can acknowledge each packet.  This example shows strict
mode (raise on any error) and non-strict mode (log warnings, only raise
on NAK).
"""

from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteSpecialFunction, WriteText
from alphasign.exceptions import NAKError, ProtocolError, TimeoutError
from alphasign.protocol import DisplayMode

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)


def send(cmd):
    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(cmd)
    sign.send(pkt)


# First, tell the sign to enable ACK/NAK responses.
send(WriteSpecialFunction.enable_ack_nak(enabled=True))

# Enable strict mode on our side: TimeoutError and ProtocolError are raised.
sign.enable_ack_nak(strict=True)

try:
    send(WriteText(b"Strict mode test", label="0", mode=DisplayMode.HOLD))
    print("Sign acknowledged the packet.")
except NAKError as e:
    print(f"Sign rejected the packet: {e}")
except TimeoutError:
    print("No response from sign (timeout).")
except ProtocolError as e:
    print(f"Unexpected response: {e}")

# Switch to non-strict mode: only NAKError is raised; timeouts are logged.
sign.enable_ack_nak(strict=False)

try:
    send(WriteText(b"Non-strict mode", label="0", mode=DisplayMode.HOLD))
    print("Packet sent (any timeout was silently ignored).")
except NAKError as e:
    print(f"Sign rejected the packet: {e}")

sign.close()
