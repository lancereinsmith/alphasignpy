"""Tests for AlphaVision bulletin commands."""

from __future__ import annotations

import pytest

from alphasign.commands.bulletin import StopBulletin, WriteBulletin
from alphasign.exceptions import InvalidParameterError
from alphasign.protocol import BulletinJustification, BulletinPosition, CommandCode

# ---------------------------------------------------------------------------
# WriteBulletin
# ---------------------------------------------------------------------------


def test_write_bulletin_command_code():
    assert WriteBulletin.code == CommandCode.WRITE_BULLETIN.value


def test_write_bulletin_basic():
    cmd = WriteBulletin("SALE TODAY")
    data = cmd.to_bytes()
    assert b"SALE TODAY" in data


def test_write_bulletin_position_top():
    cmd = WriteBulletin("Test", position=BulletinPosition.TOP)
    assert cmd.to_bytes().startswith(BulletinPosition.TOP.value)


def test_write_bulletin_position_bottom():
    cmd = WriteBulletin("Test", position=BulletinPosition.BOTTOM)
    assert cmd.to_bytes().startswith(BulletinPosition.BOTTOM.value)


def test_write_bulletin_justification_center():
    cmd = WriteBulletin(
        "Test",
        position=BulletinPosition.TOP,
        justification=BulletinJustification.CENTER,
    )
    data = cmd.to_bytes()
    assert BulletinJustification.CENTER.value in data


def test_write_bulletin_justification_right():
    cmd = WriteBulletin(
        "Test",
        position=BulletinPosition.TOP,
        justification=BulletinJustification.RIGHT,
    )
    data = cmd.to_bytes()
    assert BulletinJustification.RIGHT.value in data


def test_write_bulletin_text_too_long():
    with pytest.raises(InvalidParameterError, match="exceeds maximum"):
        WriteBulletin("x" * 226)


def test_write_bulletin_width_auto_calculated():
    # 18 chars → rounded up to 32
    cmd = WriteBulletin("SALE TODAY 50% OFF")
    assert cmd.width == 32


def test_write_bulletin_width_explicit():
    cmd = WriteBulletin("ABC", width=64)
    assert cmd.width == 64


def test_write_bulletin_count_in_output():
    cmd = WriteBulletin("Test", count=3)
    data = cmd.to_bytes()
    assert b"03" in data


def test_write_bulletin_bytes_input():
    cmd = WriteBulletin(b"bytes input")
    assert b"bytes input" in cmd.to_bytes()


def test_write_bulletin_structure():
    """Full structure: position + justification + width(2) + count(2) + text."""
    cmd = WriteBulletin(
        "HI",
        position=BulletinPosition.TOP,
        justification=BulletinJustification.LEFT,
        width=32,
        count=1,
    )
    data = cmd.to_bytes()
    assert data[0:1] == BulletinPosition.TOP.value
    assert data[1:2] == BulletinJustification.LEFT.value
    assert data[2:4] == b"20"  # 0x20 = 32 width
    assert data[4:6] == b"01"  # count = 1
    assert data[6:] == b"HI"


# ---------------------------------------------------------------------------
# StopBulletin
# ---------------------------------------------------------------------------


def test_stop_bulletin_to_bytes_empty():
    cmd = StopBulletin()
    assert cmd.to_bytes() == b""


def test_stop_bulletin_command_code():
    assert StopBulletin.code == b"OT"
