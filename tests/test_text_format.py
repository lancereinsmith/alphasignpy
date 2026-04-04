"""Tests for text_format helper functions."""

from __future__ import annotations

import pytest

from alphasign.protocol import Color, Font
from alphasign.text_format import (
    CTRL_FLASH_OFF,
    CTRL_FLASH_ON,
    CTRL_NEW_LINE,
    CTRL_NEW_PAGE,
    CTRL_TIME,
    CTRL_WIDE_OFF,
    CTRL_WIDE_ON,
    animation,
    attr,
    color,
    counter_ref,
    date_code,
    font,
    picture_ref,
    rgb_color,
    speed,
    speed_control,
    string_ref,
    temperature,
)

# ---------------------------------------------------------------------------
# color()
# ---------------------------------------------------------------------------


def test_color_red():
    assert color(Color.RED) == b"\x1c1"


def test_color_green():
    assert color(Color.GREEN) == b"\x1c2"


def test_color_rainbow1():
    assert color(Color.RAINBOW1) == b"\x1c9"


def test_color_auto():
    assert color(Color.AUTO) == b"\x1cC"


# ---------------------------------------------------------------------------
# rgb_color()
# ---------------------------------------------------------------------------


def test_rgb_color_basic():
    result = rgb_color(255, 0, 128)
    assert result == b"\x1cZ" + b"FF0080"


def test_rgb_color_shade():
    result = rgb_color(0, 128, 255, shade=True)
    assert result == b"\x1cY" + b"0080FF"


def test_rgb_color_black():
    assert rgb_color(0, 0, 0) == b"\x1cZ000000"


# ---------------------------------------------------------------------------
# font()
# ---------------------------------------------------------------------------


def test_font_five_high_std():
    assert font(Font.FIVE_HIGH_STD) == b"\x1a1"


def test_font_seven_high_std():
    assert font(Font.SEVEN_HIGH_STD) == b"\x1a3"


def test_font_custom():
    assert font(Font.FIVE_HIGH_CUSTOM) == b"\x1aW"


# ---------------------------------------------------------------------------
# speed()
# ---------------------------------------------------------------------------


def test_speed_level_1():
    assert speed(1) == b"\x15"


def test_speed_level_5():
    assert speed(5) == b"\x19"


def test_speed_level_3():
    assert speed(3) == b"\x17"


def test_speed_invalid_low():
    with pytest.raises(ValueError, match="1-5"):
        speed(0)


def test_speed_invalid_high():
    with pytest.raises(ValueError, match="1-5"):
        speed(6)


# ---------------------------------------------------------------------------
# speed_control()
# ---------------------------------------------------------------------------


def test_speed_control_level_2():
    assert speed_control(2) == b"\x092"


def test_speed_control_invalid():
    with pytest.raises(ValueError):
        speed_control(0)


# ---------------------------------------------------------------------------
# attr()
# ---------------------------------------------------------------------------


def test_attr_wide_on():
    assert attr("wide", True) == b"\x1d01"


def test_attr_wide_off():
    assert attr("wide", False) == b"\x1d00"


def test_attr_shadow_on():
    assert attr("shadow", True) == b"\x1d71"


def test_attr_unknown():
    with pytest.raises(ValueError, match="Unknown attribute"):
        attr("glowing", True)


# ---------------------------------------------------------------------------
# temperature()
# ---------------------------------------------------------------------------


def test_temperature_celsius():
    assert temperature("c") == b"\x08\x1c"


def test_temperature_fahrenheit():
    assert temperature("f") == b"\x08\x1d"


def test_temperature_default_celsius():
    assert temperature() == b"\x08\x1c"


def test_temperature_invalid():
    with pytest.raises(ValueError, match="'c' or 'f'"):
        temperature("k")


# ---------------------------------------------------------------------------
# date_code()
# ---------------------------------------------------------------------------


def test_date_mm_dd_yy():
    assert date_code("mm/dd/yy") == b"\x0b0"


def test_date_dow():
    assert date_code("dow") == b"\x0b9"


def test_date_invalid():
    with pytest.raises(ValueError, match="Unknown date format"):
        date_code("yyyy-mm-dd")


# ---------------------------------------------------------------------------
# string_ref()
# ---------------------------------------------------------------------------


def test_string_ref_returns_correct_code():
    assert string_ref("B") == b"\x10B"


def test_string_ref_invalid_length():
    with pytest.raises(ValueError):
        string_ref("AB")


# ---------------------------------------------------------------------------
# picture_ref()
# ---------------------------------------------------------------------------


def test_picture_ref():
    assert picture_ref("A") == b"\x14A"


def test_picture_ref_lowercase_upcases():
    assert picture_ref("a") == b"\x14A"


def test_picture_ref_non_alnum():
    with pytest.raises(ValueError):
        picture_ref("!")


# ---------------------------------------------------------------------------
# counter_ref()
# ---------------------------------------------------------------------------


def test_counter_ref_1():
    assert counter_ref(1) == b"\x08\x7a"


def test_counter_ref_5():
    assert counter_ref(5) == b"\x08\x7e"


def test_counter_ref_invalid():
    with pytest.raises(ValueError, match="1-5"):
        counter_ref(6)


# ---------------------------------------------------------------------------
# animation()
# ---------------------------------------------------------------------------


def test_animation_dots():
    result = animation("dots", "LOGO", hold_time=10)
    assert result.startswith(b"\x1fL")
    assert b"LOGO" in result
    assert b"000A" in result


def test_animation_quick_flick():
    result = animation("quick", "ANIM1", hold_time=0)
    assert result.startswith(b"\x1fC")


def test_animation_filename_padded():
    result = animation("dots", "A", hold_time=0)
    # Filename should be 9 chars (padded with spaces on the left)
    assert b"        A" in result


def test_animation_invalid_type():
    with pytest.raises(ValueError, match="Unknown animation type"):
        animation("spin", "FILE")


# ---------------------------------------------------------------------------
# Control code constants
# ---------------------------------------------------------------------------


def test_ctrl_flash_on():
    assert CTRL_FLASH_ON == b"\x071"


def test_ctrl_flash_off():
    assert CTRL_FLASH_OFF == b"\x070"


def test_ctrl_new_line():
    assert CTRL_NEW_LINE == b"\x0d"


def test_ctrl_new_page():
    assert CTRL_NEW_PAGE == b"\x0c"


def test_ctrl_time():
    assert CTRL_TIME == b"\x13"


def test_ctrl_wide_on():
    assert CTRL_WIDE_ON == b"\x12"


def test_ctrl_wide_off():
    assert CTRL_WIDE_OFF == b"\x11"
