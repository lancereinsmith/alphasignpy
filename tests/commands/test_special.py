"""Tests for WriteSpecialFunction and ReadSpecialFunction."""

from __future__ import annotations

import pytest

from alphasign.commands.special import ReadSpecialFunction, WriteSpecialFunction
from alphasign.exceptions import InvalidParameterError
from alphasign.protocol import (
    CommandCode,
    DayOfWeek,
    DotsColorDepth,
    FileProtection,
    FileType,
    SpecialFunction,
    TimeFormat,
)

# ---------------------------------------------------------------------------
# Command code
# ---------------------------------------------------------------------------


def test_write_special_command_code():
    cmd = WriteSpecialFunction.soft_reset()
    assert cmd.code == CommandCode.WRITE_SPECIAL.value


def test_read_special_command_code():
    cmd = ReadSpecialFunction(SpecialFunction.SET_TIME)
    assert cmd.code == CommandCode.READ_SPECIAL.value


# ---------------------------------------------------------------------------
# set_time()
# ---------------------------------------------------------------------------


def test_set_time_basic():
    cmd = WriteSpecialFunction.set_time(14, 30)
    data = cmd.to_bytes()
    assert data == b" 1430"


def test_set_time_midnight():
    cmd = WriteSpecialFunction.set_time(0, 0)
    assert cmd.to_bytes() == b" 0000"


def test_set_time_invalid_hours():
    with pytest.raises(InvalidParameterError, match="hours"):
        WriteSpecialFunction.set_time(24, 0)


def test_set_time_invalid_minutes():
    with pytest.raises(InvalidParameterError, match="minutes"):
        WriteSpecialFunction.set_time(12, 60)


# ---------------------------------------------------------------------------
# set_date()
# ---------------------------------------------------------------------------


def test_set_date_basic():
    cmd = WriteSpecialFunction.set_date(12, 25, 24)
    data = cmd.to_bytes()
    assert data == b";122524"


def test_set_date_invalid_month():
    with pytest.raises(InvalidParameterError, match="month"):
        WriteSpecialFunction.set_date(13, 1, 24)


def test_set_date_invalid_day():
    with pytest.raises(InvalidParameterError, match="day"):
        WriteSpecialFunction.set_date(1, 32, 24)


# ---------------------------------------------------------------------------
# set_day_of_week()
# ---------------------------------------------------------------------------


def test_set_day_of_week_monday():
    cmd = WriteSpecialFunction.set_day_of_week(DayOfWeek.MONDAY)
    assert cmd.to_bytes() == b"&2"


def test_set_day_of_week_sunday():
    cmd = WriteSpecialFunction.set_day_of_week(DayOfWeek.SUNDAY)
    assert cmd.to_bytes() == b"&1"


# ---------------------------------------------------------------------------
# set_time_format()
# ---------------------------------------------------------------------------


def test_set_time_format_standard():
    cmd = WriteSpecialFunction.set_time_format(TimeFormat.STANDARD)
    assert cmd.to_bytes() == b"'S"


def test_set_time_format_military():
    cmd = WriteSpecialFunction.set_time_format(TimeFormat.MILITARY)
    assert cmd.to_bytes() == b"'M"


# ---------------------------------------------------------------------------
# set_speaker()
# ---------------------------------------------------------------------------


def test_set_speaker_on():
    cmd = WriteSpecialFunction.set_speaker(True)
    assert cmd.to_bytes() == b"!00"


def test_set_speaker_off():
    cmd = WriteSpecialFunction.set_speaker(False)
    assert cmd.to_bytes() == b"!FF"


# ---------------------------------------------------------------------------
# generate_tone()
# ---------------------------------------------------------------------------


def test_generate_tone_preset():
    cmd = WriteSpecialFunction.generate_tone(1)
    data = cmd.to_bytes()
    assert data == b"(\x31"


def test_generate_tone_variable():
    cmd = WriteSpecialFunction.generate_tone(2, frequency=0x20, duration=5, repeat=2)
    data = cmd.to_bytes()
    assert data == b"(\x32" + b"205" + b"2"


def test_generate_tone_invalid_type():
    with pytest.raises(InvalidParameterError, match="tone_type"):
        WriteSpecialFunction.generate_tone(3)


# ---------------------------------------------------------------------------
# clear_memory()
# ---------------------------------------------------------------------------


def test_clear_memory():
    cmd = WriteSpecialFunction.clear_memory()
    assert cmd.to_bytes() == b"$$$$"


# ---------------------------------------------------------------------------
# configure_memory()
# ---------------------------------------------------------------------------


def test_configure_memory_text_file():
    cmd = WriteSpecialFunction.configure_memory(
        [
            {
                "label": "A",
                "type": FileType.TEXT,
                "protection": FileProtection.UNLOCKED,
                "size": 256,
                "start_time": 0xFF,
                "stop_time": 0xFF,
            }
        ]
    )
    data = cmd.to_bytes()
    assert data.startswith(b"$A")
    assert b"AU" in data  # type=TEXT, protection=UNLOCKED
    assert b"0100" in data  # 256 = 0x0100


def test_configure_memory_string_file():
    cmd = WriteSpecialFunction.configure_memory(
        [{"label": "B", "type": FileType.STRING, "size": 64}]
    )
    data = cmd.to_bytes()
    assert b"BU" in data
    assert b"0000" in data  # string placeholder


def test_configure_memory_dots_file():
    cmd = WriteSpecialFunction.configure_memory(
        [
            {
                "label": "P",
                "type": FileType.DOTS,
                "size": (16, 60),
                "color_depth": DotsColorDepth.EIGHT_COLOR,
            }
        ]
    )
    data = cmd.to_bytes()
    assert b"PD" in data
    assert DotsColorDepth.EIGHT_COLOR.value in data


def test_configure_memory_multiple_files():
    cmd = WriteSpecialFunction.configure_memory(
        [
            {"label": "A", "type": FileType.TEXT, "size": 128},
            {"label": "B", "type": FileType.STRING, "size": 32},
        ]
    )
    data = cmd.to_bytes()
    assert b"A" in data
    assert b"B" in data


# ---------------------------------------------------------------------------
# set_run_time_table()
# ---------------------------------------------------------------------------


def test_set_run_time_table():
    cmd = WriteSpecialFunction.set_run_time_table("A", 0x30, 0x60)
    data = cmd.to_bytes()
    assert b")" in data
    assert b"A" in data


def test_set_run_time_table_invalid_code():
    with pytest.raises(InvalidParameterError, match="Time codes"):
        WriteSpecialFunction.set_run_time_table("A", 0x100, 0x00)


# ---------------------------------------------------------------------------
# set_dimming_register()
# ---------------------------------------------------------------------------


def test_set_dimming_register_100_percent():
    cmd = WriteSpecialFunction.set_dimming_register(0, 100)
    data = cmd.to_bytes()
    assert b"/" in data
    assert b"00" in data  # index 0 = 100%


def test_set_dimming_register_rounds_to_nearest():
    # 80% is closest to 86
    cmd = WriteSpecialFunction.set_dimming_register(0, 80)
    data = cmd.to_bytes()
    assert b"01" in data  # index 1 = 86%


def test_set_dimming_register_invalid():
    with pytest.raises(InvalidParameterError, match="brightness_percent"):
        WriteSpecialFunction.set_dimming_register(0, 101)


# ---------------------------------------------------------------------------
# soft_reset()
# ---------------------------------------------------------------------------


def test_soft_reset():
    cmd = WriteSpecialFunction.soft_reset()
    assert cmd.to_bytes() == b","


# ---------------------------------------------------------------------------
# enable_ack_nak()
# ---------------------------------------------------------------------------


def test_enable_ack_nak_true():
    cmd = WriteSpecialFunction.enable_ack_nak(True)
    assert cmd.to_bytes() == b"s1"


def test_enable_ack_nak_false():
    cmd = WriteSpecialFunction.enable_ack_nak(False)
    assert cmd.to_bytes() == b"s0"


# ---------------------------------------------------------------------------
# set_serial_address()
# ---------------------------------------------------------------------------


def test_set_serial_address_valid():
    cmd = WriteSpecialFunction.set_serial_address("0A")
    assert b"70A" in cmd.to_bytes()


def test_set_serial_address_invalid():
    with pytest.raises(InvalidParameterError, match="2 hex characters"):
        WriteSpecialFunction.set_serial_address("001")


# ---------------------------------------------------------------------------
# ReadSpecialFunction
# ---------------------------------------------------------------------------


def test_read_special_set_time():
    cmd = ReadSpecialFunction(SpecialFunction.SET_TIME)
    assert cmd.to_bytes() == SpecialFunction.SET_TIME.value


def test_read_special_general_info():
    cmd = ReadSpecialFunction(SpecialFunction.GENERAL_INFO)
    assert cmd.to_bytes() == SpecialFunction.GENERAL_INFO.value
