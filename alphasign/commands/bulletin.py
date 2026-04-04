"""AlphaVision Bulletin commands (O / OT).

Bulletin messages are displayed on AlphaVision matrix signs.  They support
top/bottom positioning and left/centre/right justification.

Protocol reference: sections 3.15 (Write Bulletin) and 3.16 (Stop Bulletin).
"""

from __future__ import annotations

from ..exceptions import InvalidParameterError
from ..protocol import (
    BulletinJustification,
    BulletinPosition,
    CommandCode,
)
from .base import BaseCommand

_MAX_TEXT_LEN = 225


class WriteBulletin(BaseCommand):
    """Write an AlphaVision Bulletin message (command ``O``).

    Args:
        text: Message text (up to 225 ASCII chars).  Only colour control codes
            are permitted (no font, mode, or other control codes).
        position: :class:`~alphasign.protocol.BulletinPosition` — ``TOP`` or
            ``BOTTOM``.
        justification: :class:`~alphasign.protocol.BulletinJustification` —
            ``LEFT``, ``CENTER``, or ``RIGHT``.
        width: Message character count, rounded up to the nearest 32-column
            boundary.  Pass ``0`` to calculate automatically.
        count: Number of times to display the message (0-0xFF).

    Raises:
        InvalidParameterError: If *text* exceeds 225 characters.

    Example::

        from alphasign.commands.bulletin import WriteBulletin
        from alphasign.protocol import BulletinPosition, BulletinJustification

        cmd = WriteBulletin(
            "SALE TODAY 50% OFF",
            position=BulletinPosition.TOP,
            justification=BulletinJustification.CENTER,
        )
    """

    code = CommandCode.WRITE_BULLETIN.value

    def __init__(
        self,
        text: str | bytes,
        position: BulletinPosition = BulletinPosition.TOP,
        justification: BulletinJustification = BulletinJustification.LEFT,
        width: int = 0,
        count: int = 1,
    ) -> None:
        text_bytes = text.encode("ascii", errors="replace") if isinstance(text, str) else text
        if len(text_bytes) > _MAX_TEXT_LEN:
            raise InvalidParameterError(
                f"Bulletin text length {len(text_bytes)} exceeds maximum of {_MAX_TEXT_LEN}."
            )
        self.text = text_bytes
        self.position = position
        self.justification = justification
        # Round width up to nearest 32-column boundary
        if width == 0:
            char_count = len(text_bytes)
            width = ((char_count + 31) // 32) * 32 or 32
        self.width = width
        self.count = count

    def to_bytes(self) -> bytes:
        return (
            self.position.value
            + self.justification.value
            + f"{self.width:02X}".encode()
            + f"{self.count:02X}".encode()
            + self.text
        )


class StopBulletin(BaseCommand):
    """Stop an AlphaVision Bulletin message (command ``OT``).

    Send this to halt a bulletin that is currently being displayed.
    """

    # AlphaVision bulletin stop uses two-byte command code "OT"
    code = CommandCode.WRITE_BULLETIN.value + b"T"

    def to_bytes(self) -> bytes:
        return b""
