"""Write TEXT (command A) and Read TEXT (command B).

The TEXT file is the primary message container on an Alpha sign.  A sign
may hold multiple labelled TEXT files in its battery-backed memory.  The
*priority* file (label ``"0"``) always exists and overrides other files
immediately on receipt.

Protocol reference: sections 3.1 (Write TEXT) and 3.2 (Read TEXT).
"""

from __future__ import annotations

from ..exceptions import InvalidParameterError
from ..protocol import (
    ESC,
    CommandCode,
    DisplayMode,
    DisplayPosition,
    SpecialMode,
)
from .base import BaseCommand

# Valid file label range: printable ASCII 20H-7FH excluding "?" and (for
# counter-equipped signs) "1"-"5".
_VALID_LABEL_MIN = 0x20
_VALID_LABEL_MAX = 0x7F


def _validate_label(label: str) -> None:
    if len(label) != 1:
        raise InvalidParameterError(f"File label must be exactly 1 character, got {label!r}.")
    code = ord(label)
    if code < _VALID_LABEL_MIN or code > _VALID_LABEL_MAX:
        raise InvalidParameterError(f"File label {label!r} is outside the valid range 0x20-0x7F.")
    if label == "?":
        raise InvalidParameterError("'?' is reserved as a wildcard and cannot be a file label.")


class WriteText(BaseCommand):
    """Write a TEXT file to the sign (command ``A``).

    Args:
        message: The text to display.  May contain embedded control bytes
            from :mod:`alphasign.text_format`.
        label: One-character file label.  Use ``"0"`` for the priority file
            (always available, no memory configuration required) or a letter
            ``"A"``-``"Z"`` for a configured file.
        position: Vertical display position.  Defaults to
            :attr:`~alphasign.protocol.DisplayPosition.FILL`.
        mode: Display / transition mode.  Defaults to
            :attr:`~alphasign.protocol.DisplayMode.ROTATE`.
        special_mode: Required when *mode* is
            :attr:`~alphasign.protocol.DisplayMode.SPECIAL`.

    Example::

        from alphasign.commands.text import WriteText
        from alphasign.protocol import DisplayMode, Color

        cmd = WriteText(
            Color.RED.value + b"Hello, world!",
            label="A",
            mode=DisplayMode.HOLD,
        )
    """

    code = CommandCode.WRITE_TEXT.value

    def __init__(
        self,
        message: str | bytes,
        label: str = "A",
        position: DisplayPosition = DisplayPosition.FILL,
        mode: DisplayMode = DisplayMode.ROTATE,
        special_mode: SpecialMode | None = None,
    ) -> None:
        _validate_label(label)
        if mode is DisplayMode.SPECIAL and special_mode is None:
            raise InvalidParameterError(
                "special_mode must be provided when mode is DisplayMode.SPECIAL."
            )
        self.message = message.encode() if isinstance(message, str) else message
        self.label = label
        self.position = position
        self.mode = mode
        self.special_mode = special_mode

    def to_bytes(self) -> bytes:
        data = self.label.encode()
        data += ESC
        data += self.position.value
        data += self.mode.value
        if self.mode is DisplayMode.SPECIAL and self.special_mode is not None:
            data += self.special_mode.value
        data += self.message
        return data


class ReadText(BaseCommand):
    """Request the sign to return the contents of a TEXT file (command ``B``).

    Args:
        label: The label of the TEXT file to read.

    The sign's response is a full Write TEXT packet.  Parse it with
    :func:`parse_read_text_response`.
    """

    code = CommandCode.READ_TEXT.value

    def __init__(self, label: str = "A") -> None:
        _validate_label(label)
        self.label = label

    def to_bytes(self) -> bytes:
        return self.label.encode()


def parse_read_text_response(
    response: bytes,
) -> tuple[str, DisplayPosition, DisplayMode, bytes]:
    """Parse a sign's response to a :class:`ReadText` command.

    Args:
        response: The raw bytes received from the sign (full packet including
            framing).

    Returns:
        A tuple of ``(label, position, mode, message)`` where *message* is
        the raw ASCII + control-code byte string.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    # Response format: 20x NUL, SOH, type "0", addr "00", STX, "A", label,
    # ESC, position, mode, [special], message, ETX, checksum, EOT
    try:
        stx_idx = response.index(b"\x02")
        payload = response[stx_idx + 1 :]
        if not payload or payload[0:1] != CommandCode.WRITE_TEXT.value:
            raise ValueError("Response does not contain a Write TEXT command code.")
        label = chr(payload[1])
        if payload[2:3] != ESC:
            raise ValueError("Expected ESC byte at position 2 of TEXT response payload.")
        position_byte = payload[3:4]
        mode_byte = payload[4:5]
        try:
            position = DisplayPosition(position_byte)
        except ValueError:
            position = DisplayPosition.FILL
        try:
            mode = DisplayMode(mode_byte)
        except ValueError:
            mode = DisplayMode.ROTATE
        msg_start = 5
        # Find ETX or EOT to end message
        etx_idx = payload.find(b"\x03", msg_start)
        eot_idx = payload.find(b"\x04", msg_start)
        end = min(
            (i for i in [etx_idx, eot_idx] if i >= 0),
            default=len(payload),
        )
        message = payload[msg_start:end]
        return label, position, mode, message
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Could not parse Read TEXT response: {exc}") from exc
