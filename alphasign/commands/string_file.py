"""Write STRING (command G) and Read STRING (command H).

STRING files store a short variable text string (up to ~125 bytes) that can
be *embedded inside* a TEXT file message.  A TEXT message references a
STRING file with the control code ``0x10 + label``.

Protocol reference: sections 3.7 (Write STRING) and 3.8 (Read STRING).
"""

from __future__ import annotations

from ..exceptions import InvalidParameterError
from ..protocol import CommandCode
from .base import BaseCommand

_MAX_STRING_LEN = 125

# STRING-file embedded control codes (used *inside* the string data)
CTRL_NO_HOLD_SPEED = b"\x09"
CTRL_NEWLINE = b"\x0d"
CTRL_WIDE_OFF = b"\x11"
CTRL_WIDE_ON = b"\x12"
CTRL_TIME = b"\x13"
CTRL_SPEED_1 = b"\x15"
CTRL_SPEED_2 = b"\x16"
CTRL_SPEED_3 = b"\x17"
CTRL_SPEED_4 = b"\x18"  # default
CTRL_SPEED_5 = b"\x19"
CTRL_CHARSET = b"\x1a"
CTRL_COLOR = b"\x1c"
CTRL_SPACING = b"\x1e"


def _validate_string_label(label: str) -> None:
    if len(label) != 1:
        raise InvalidParameterError(
            f"STRING file label must be exactly 1 character, got {label!r}."
        )
    code = ord(label)
    if code < 0x20 or code > 0x7F:
        raise InvalidParameterError(
            f"STRING file label {label!r} is outside the valid range 0x20-0x7F."
        )
    if label == "?":
        raise InvalidParameterError(
            "'?' is reserved as a wildcard and cannot be a STRING file label."
        )


class WriteString(BaseCommand):
    """Write a STRING variable file (command ``G``).

    Args:
        data: The string content.  May be a plain Python string (encoded as
            ASCII) or raw bytes containing the allowed control codes.
        label: One-character file label (must be pre-configured in memory).

    Note:
        Rainbow colour control codes (``Rain1``, ``Rain2``) do **not** work
        inside STRING files — use plain colour codes only.

    Example::

        from alphasign.commands.string_file import WriteString

        # Update string variable "B" with a live temperature reading
        cmd = WriteString("22.5°C", label="B")
    """

    code = CommandCode.WRITE_STRING.value

    def __init__(self, data: str | bytes, label: str = "A") -> None:
        _validate_string_label(label)
        raw = data.encode("ascii", errors="replace") if isinstance(data, str) else data
        if len(raw) > _MAX_STRING_LEN:
            raise InvalidParameterError(
                f"STRING data length {len(raw)} exceeds maximum of {_MAX_STRING_LEN} bytes."
            )
        self.data = raw
        self.label = label

    def to_bytes(self) -> bytes:
        return self.label.encode() + self.data


class ReadString(BaseCommand):
    """Request the sign to return a STRING file (command ``H``).

    Args:
        label: The label of the STRING file to read.

    The sign's response is a full Write STRING packet.  Parse it with
    :func:`parse_read_string_response`.
    """

    code = CommandCode.READ_STRING.value

    def __init__(self, label: str = "A") -> None:
        _validate_string_label(label)
        self.label = label

    def to_bytes(self) -> bytes:
        return self.label.encode()


def parse_read_string_response(response: bytes) -> tuple[str, bytes]:
    """Parse a sign's response to a :class:`ReadString` command.

    Args:
        response: Raw bytes from the sign (full packet).

    Returns:
        A tuple of ``(label, data)`` where *data* is the raw string content.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    try:
        stx_idx = response.index(b"\x02")
        payload = response[stx_idx + 1 :]
        if payload[0:1] != CommandCode.WRITE_STRING.value:
            raise ValueError("Response does not contain a Write STRING command code.")
        label = chr(payload[1])
        end = next(
            (i for i, b in enumerate(payload[2:], 2) if b in (0x03, 0x04)),
            len(payload),
        )
        return label, payload[2:end]
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Could not parse Read STRING response: {exc}") from exc
