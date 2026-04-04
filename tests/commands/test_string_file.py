"""Tests for WriteString and ReadString commands."""

from __future__ import annotations

import pytest

from alphasign.commands.string_file import ReadString, WriteString, parse_read_string_response
from alphasign.exceptions import InvalidParameterError
from alphasign.protocol import CommandCode

# ---------------------------------------------------------------------------
# WriteString
# ---------------------------------------------------------------------------


def test_write_string_basic():
    cmd = WriteString("Hello", label="A")
    data = cmd.to_bytes()
    assert data == b"AHello"


def test_write_string_bytes_input():
    cmd = WriteString(b"raw bytes", label="B")
    assert b"raw bytes" in cmd.to_bytes()


def test_write_string_label_in_output():
    cmd = WriteString("test", label="C")
    assert cmd.to_bytes().startswith(b"C")


def test_write_string_command_code():
    assert WriteString.code == CommandCode.WRITE_STRING.value


def test_write_string_exceeds_max_length():
    with pytest.raises(InvalidParameterError, match="exceeds maximum"):
        WriteString("x" * 200)


def test_write_string_invalid_label():
    with pytest.raises(InvalidParameterError):
        WriteString("hi", label="?")


def test_write_string_label_too_long():
    with pytest.raises(InvalidParameterError, match="exactly 1 character"):
        WriteString("hi", label="AB")


# ---------------------------------------------------------------------------
# ReadString
# ---------------------------------------------------------------------------


def test_read_string_to_bytes():
    cmd = ReadString(label="A")
    assert cmd.to_bytes() == b"A"


def test_read_string_command_code():
    assert ReadString.code == CommandCode.READ_STRING.value


def test_read_string_invalid_label():
    with pytest.raises(InvalidParameterError):
        ReadString(label="?")


# ---------------------------------------------------------------------------
# parse_read_string_response()
# ---------------------------------------------------------------------------


def _build_string_response(label: str, data: bytes) -> bytes:
    payload = b"G" + label.encode() + data
    return b"\x00" * 20 + b"\x01" + b"0" + b"00" + b"\x02" + payload + b"\x03" + b"0000" + b"\x04"


def test_parse_string_response_label():
    resp = _build_string_response("B", b"temperature=22.5")
    label, _ = parse_read_string_response(resp)
    assert label == "B"


def test_parse_string_response_data():
    resp = _build_string_response("A", b"hello world")
    _, data = parse_read_string_response(resp)
    assert data == b"hello world"


def test_parse_string_response_invalid():
    with pytest.raises(ValueError):
        parse_read_string_response(b"not a response")
