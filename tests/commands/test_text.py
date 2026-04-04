"""Tests for WriteText and ReadText commands."""

from __future__ import annotations

import pytest

from alphasign.commands.text import ReadText, WriteText, parse_read_text_response
from alphasign.exceptions import InvalidParameterError
from alphasign.protocol import (
    ESC,
    CommandCode,
    DisplayMode,
    DisplayPosition,
    SpecialMode,
)

# ---------------------------------------------------------------------------
# WriteText — label validation
# ---------------------------------------------------------------------------


def test_write_text_valid_label():
    cmd = WriteText(b"Hello", label="A")
    assert cmd.label == "A"


def test_write_text_label_too_long():
    with pytest.raises(InvalidParameterError, match="exactly 1 character"):
        WriteText(b"Hi", label="AB")


def test_write_text_label_wildcard():
    with pytest.raises(InvalidParameterError, match="wildcard"):
        WriteText(b"Hi", label="?")


def test_write_text_label_out_of_range():
    with pytest.raises(InvalidParameterError):
        WriteText(b"Hi", label="\x01")


# ---------------------------------------------------------------------------
# WriteText — mode + special mode
# ---------------------------------------------------------------------------


def test_write_text_special_mode_required():
    with pytest.raises(InvalidParameterError, match="special_mode"):
        WriteText(b"Hi", mode=DisplayMode.SPECIAL)


def test_write_text_special_mode_included():
    cmd = WriteText(b"Twinkle", mode=DisplayMode.SPECIAL, special_mode=SpecialMode.TWINKLE)
    data = cmd.to_bytes()
    assert DisplayMode.SPECIAL.value in data
    assert SpecialMode.TWINKLE.value in data


def test_write_text_no_special_mode_for_non_special():
    cmd = WriteText(b"Test", mode=DisplayMode.HOLD)
    data = cmd.to_bytes()
    assert DisplayMode.HOLD.value in data


# ---------------------------------------------------------------------------
# WriteText — to_bytes() structure
# ---------------------------------------------------------------------------


def test_write_text_to_bytes_starts_with_label():
    cmd = WriteText(b"Hi", label="B")
    data = cmd.to_bytes()
    assert data.startswith(b"B")


def test_write_text_to_bytes_contains_esc():
    cmd = WriteText(b"Hi")
    data = cmd.to_bytes()
    assert ESC in data


def test_write_text_to_bytes_contains_message():
    cmd = WriteText(b"Hello, world!")
    data = cmd.to_bytes()
    assert b"Hello, world!" in data


def test_write_text_string_message_encoded():
    cmd = WriteText("Hello")
    data = cmd.to_bytes()
    assert b"Hello" in data


def test_write_text_position_fill():
    cmd = WriteText(b"X", position=DisplayPosition.FILL)
    data = cmd.to_bytes()
    assert DisplayPosition.FILL.value in data


def test_write_text_position_top_line():
    cmd = WriteText(b"X", position=DisplayPosition.TOP_LINE)
    data = cmd.to_bytes()
    assert DisplayPosition.TOP_LINE.value in data


def test_write_text_command_code():
    assert WriteText.code == CommandCode.WRITE_TEXT.value


# ---------------------------------------------------------------------------
# WriteText — priority file
# ---------------------------------------------------------------------------


def test_write_text_priority_label():
    cmd = WriteText(b"Priority!", label="0")
    data = cmd.to_bytes()
    assert data.startswith(b"0")


# ---------------------------------------------------------------------------
# ReadText
# ---------------------------------------------------------------------------


def test_read_text_to_bytes_returns_label():
    cmd = ReadText(label="A")
    assert cmd.to_bytes() == b"A"


def test_read_text_command_code():
    assert ReadText.code == CommandCode.READ_TEXT.value


def test_read_text_invalid_label():
    with pytest.raises(InvalidParameterError):
        ReadText(label="?")


# ---------------------------------------------------------------------------
# parse_read_text_response()
# ---------------------------------------------------------------------------


def _build_response(
    label: str, position: DisplayPosition, mode: DisplayMode, message: bytes
) -> bytes:
    """Build a mock sign response packet for Read TEXT."""
    payload = b"A" + label.encode() + ESC + position.value + mode.value + message
    return (
        b"\x00" * 20
        + b"\x01"  # SOH
        + b"0"
        + b"00"
        + b"\x02"  # STX
        + payload
        + b"\x03"  # ETX
        + b"0000"  # checksum placeholder
        + b"\x04"  # EOT
    )


def test_parse_read_text_response_label():
    resp = _build_response("A", DisplayPosition.FILL, DisplayMode.ROTATE, b"Hello")
    label, _, _, _ = parse_read_text_response(resp)
    assert label == "A"


def test_parse_read_text_response_message():
    resp = _build_response("A", DisplayPosition.FILL, DisplayMode.HOLD, b"World")
    _, _, _, msg = parse_read_text_response(resp)
    assert msg == b"World"


def test_parse_read_text_response_mode():
    resp = _build_response("A", DisplayPosition.FILL, DisplayMode.FLASH, b"X")
    _, _, mode, _ = parse_read_text_response(resp)
    assert mode is DisplayMode.FLASH


def test_parse_read_text_response_invalid():
    with pytest.raises(ValueError):
        parse_read_text_response(b"garbage data")
