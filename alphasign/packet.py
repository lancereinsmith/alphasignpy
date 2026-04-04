"""Standard Transmission Packet builder.

A :class:`Packet` holds one or more commands and serialises them according
to the Alpha Sign Communications Protocol framing format::

    [5x NUL] [SOH] [TypeCode] [SignAddress]
    ( [STX] [CmdCode] [CmdData] [ETX] [Checksum] ) …
    [EOT]

Checksums are optional per-command and are calculated as the 16-bit
unsigned sum of all bytes from STX through ETX inclusive, formatted as four
upper-case ASCII hex digits.

The special byte ``DELAY`` (0xFF) is used as a *timing marker* only.  It is
never transmitted to the sign; instead :meth:`~alphasign.sign.Sign.send`
splits on it and sleeps 100 ms between parts.  Checksums are therefore
computed on data **excluding** all DELAY markers.
"""

from __future__ import annotations

from .commands.base import BaseCommand
from .protocol import BROADCAST_ADDRESS, DELAY, EOT, ETX, SOH, STX, SYNC


class Packet:
    """Build a protocol-compliant transmission packet.

    Args:
        type_code: One-byte sign type code (e.g. ``b"Z"`` for all signs).
        address: Two-character hex sign address (e.g. ``"00"`` for broadcast).

    Example::

        pkt = Packet(type_code=b"Z", address="00")
        pkt.add(WriteText("Hello"))
        sign.send(pkt)
    """

    def __init__(
        self,
        type_code: bytes = b"Z",
        address: str = BROADCAST_ADDRESS,
    ) -> None:
        self.type_code = type_code
        self.address = address
        self._commands: list[tuple[bytes, bytes, bool]] = []
        # Each entry: (command_code, command_data, use_checksum)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(
        self,
        command: BaseCommand,
        *,
        checksum: bool = True,
    ) -> Packet:
        """Append *command* to the packet.

        *command* must have a ``.code`` attribute (``bytes``) and a
        ``.to_bytes()`` method that returns ``bytes``.

        Args:
            command: Any command object (WriteText, WriteSpecialFunction, …).
            checksum: Include a checksum for this command (default ``True``).

        Returns:
            ``self`` for chaining.
        """
        code: bytes = command.code
        data: bytes = command.to_bytes()
        self._commands.append((code, data, checksum))
        return self

    def to_bytes(self) -> bytes:
        """Serialise the packet to a byte string ready to be sent."""
        out = SYNC + SOH + self.type_code + self.address.encode()

        for code, data, use_checksum in self._commands:
            # STX then optional DELAY marker (signals 100 ms pause to send())
            out += STX + DELAY
            out += code + data

            # ETX required when using checksum or when nesting (>1 command)
            if use_checksum or len(self._commands) > 1:
                out += ETX
                if use_checksum:
                    out += self._checksum(code, data)

        out += EOT
        return out

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _checksum(code: bytes, data: bytes) -> bytes:
        """Return the 4-char ASCII hex checksum for one command.

        Computed as the 16-bit unsigned sum of:
        ``STX + code + data + ETX``
        with all DELAY (0xFF) markers stripped first.
        """
        clean = (STX + code + data + ETX).replace(DELAY, b"")
        total = sum(clean) % 65536
        return f"{total:04X}".encode()
