"""Tests for DOTS picture commands (Small, Large, RGB)."""

from __future__ import annotations

import pytest

from alphasign.commands.dots import (
    ReadLargeDots,
    ReadRGBDots,
    ReadSmallDots,
    WriteLargeDots,
    WriteRGBDots,
    WriteSmallDots,
    build_pixel_row,
    build_rgb_row,
)
from alphasign.exceptions import InvalidParameterError
from alphasign.protocol import DELAY, CommandCode, PixelColor

# ---------------------------------------------------------------------------
# WriteSmallDots
# ---------------------------------------------------------------------------


def test_small_dots_command_code():
    assert WriteSmallDots.code == CommandCode.WRITE_SMALL_DOTS.value


def test_small_dots_to_bytes_structure():
    data = b"1" * 10 + b"\r"
    cmd = WriteSmallDots(data, label="A", width=10, height=1)
    result = cmd.to_bytes()
    assert result.startswith(b"A")
    assert b"01" in result  # height hex
    assert b"0A" in result  # width hex
    assert DELAY in result


def test_small_dots_height_too_large():
    with pytest.raises(InvalidParameterError, match="height"):
        WriteSmallDots(b"", label="A", width=10, height=32)


def test_small_dots_width_too_large():
    with pytest.raises(InvalidParameterError, match="width"):
        WriteSmallDots(b"", label="A", width=256, height=1)


def test_small_dots_max_height_allowed():
    cmd = WriteSmallDots(b"", label="A", width=0, height=31)
    assert cmd.height == 31


def test_small_dots_pixel_data_included():
    pixel_data = b"12345\r"
    cmd = WriteSmallDots(pixel_data, label="A", width=5, height=1)
    assert pixel_data in cmd.to_bytes()


def test_small_dots_delay_before_pixel_data():
    pixel_data = b"12345\r"
    cmd = WriteSmallDots(pixel_data, label="A", width=5, height=1)
    result = cmd.to_bytes()
    delay_idx = result.index(DELAY)
    pixel_start = result.index(pixel_data)
    assert delay_idx < pixel_start


# ---------------------------------------------------------------------------
# WriteSmallDots — compression
# ---------------------------------------------------------------------------


def test_small_dots_compress_run():
    # 5 consecutive "1" pixels → should be compressed
    pixel_data = b"11111\r"
    cmd = WriteSmallDots(pixel_data, label="A", width=5, height=1, compress=True)
    compressed = cmd._compress()
    assert b"\x11" in compressed  # run-length marker


def test_small_dots_compress_short_run_not_compressed():
    # Run of 3 — too short to compress (threshold is 4)
    pixel_data = b"111\r"
    cmd = WriteSmallDots(pixel_data, label="A", width=3, height=1, compress=True)
    compressed = cmd._compress()
    assert b"\x11" not in compressed
    assert b"111" in compressed


def test_small_dots_compress_preserves_cr():
    pixel_data = b"1234\r5678\r"
    cmd = WriteSmallDots(pixel_data, label="A", width=4, height=2, compress=True)
    result = cmd._compress()
    assert result.count(b"\r") == 2


# ---------------------------------------------------------------------------
# ReadSmallDots
# ---------------------------------------------------------------------------


def test_read_small_dots_command_code():
    assert ReadSmallDots.code == CommandCode.READ_SMALL_DOTS.value


def test_read_small_dots_to_bytes():
    cmd = ReadSmallDots(label="B")
    assert cmd.to_bytes() == b"B"


# ---------------------------------------------------------------------------
# WriteLargeDots
# ---------------------------------------------------------------------------


def test_large_dots_command_code():
    assert WriteLargeDots.code == CommandCode.WRITE_LARGE_DOTS.value


def test_large_dots_4_digit_dimensions():
    cmd = WriteLargeDots(b"", label="A", width=0x100, height=0x200)
    result = cmd.to_bytes()
    assert b"0200" in result  # height
    assert b"0100" in result  # width


def test_large_dots_dimension_overflow():
    with pytest.raises(InvalidParameterError, match="65535"):
        WriteLargeDots(b"", label="A", width=0x10000, height=1)


def test_large_dots_delay_marker_present():
    cmd = WriteLargeDots(b"data\r", label="A", width=4, height=1)
    assert DELAY in cmd.to_bytes()


# ---------------------------------------------------------------------------
# WriteRGBDots
# ---------------------------------------------------------------------------


def test_rgb_dots_command_code():
    assert WriteRGBDots.code == CommandCode.WRITE_RGB_DOTS.value


def test_rgb_dots_pixel_data():
    pixel_data = b"FF000000FF00\r"
    cmd = WriteRGBDots(pixel_data, label="A", width=2, height=1)
    assert pixel_data in cmd.to_bytes()


def test_rgb_dots_compress():
    pixel = b"FF0000"
    data = pixel * 4 + b"\r"
    cmd = WriteRGBDots(data, label="A", width=4, height=1, compress=True)
    compressed = cmd._compress()
    assert b"\x11" in compressed


# ---------------------------------------------------------------------------
# ReadLargeDots / ReadRGBDots
# ---------------------------------------------------------------------------


def test_read_large_dots():
    cmd = ReadLargeDots(label="C")
    assert cmd.to_bytes() == b"C"
    assert cmd.code == CommandCode.READ_LARGE_DOTS.value


def test_read_rgb_dots():
    cmd = ReadRGBDots(label="D")
    assert cmd.to_bytes() == b"D"
    assert cmd.code == CommandCode.READ_RGB_DOTS.value


# ---------------------------------------------------------------------------
# build_pixel_row()
# ---------------------------------------------------------------------------


def test_build_pixel_row_single():
    row = build_pixel_row([PixelColor.RED])
    assert row == b"1\r"


def test_build_pixel_row_multiple():
    row = build_pixel_row([PixelColor.RED, PixelColor.OFF, PixelColor.GREEN])
    assert row == b"102\r"


def test_build_pixel_row_ends_with_cr():
    row = build_pixel_row([PixelColor.AMBER] * 5)
    assert row.endswith(b"\r")


# ---------------------------------------------------------------------------
# build_rgb_row()
# ---------------------------------------------------------------------------


def test_build_rgb_row_basic():
    row = build_rgb_row([(255, 0, 0), (0, 255, 0)])
    assert row == b"FF0000" + b"00FF00" + b"\r"


def test_build_rgb_row_ends_with_cr():
    row = build_rgb_row([(0, 0, 0)])
    assert row.endswith(b"\r")
