"""Alpha Sign command classes.

All command classes are re-exported here for convenience::

    from alphasign.commands import WriteText, WriteSpecialFunction, WriteSmallDots
"""

from __future__ import annotations

from .bulletin import StopBulletin, WriteBulletin
from .dots import (
    ReadLargeDots,
    ReadRGBDots,
    ReadSmallDots,
    WriteLargeDots,
    WriteRGBDots,
    WriteSmallDots,
    build_pixel_row,
    build_rgb_row,
)
from .special import ReadSpecialFunction, WriteSpecialFunction, parse_general_info
from .string_file import ReadString, WriteString
from .text import ReadText, WriteText, parse_read_text_response

__all__ = [  # noqa: RUF022
    # Text
    "WriteText",
    "ReadText",
    "parse_read_text_response",
    # String
    "WriteString",
    "ReadString",
    # Dots
    "WriteSmallDots",
    "ReadSmallDots",
    "WriteLargeDots",
    "ReadLargeDots",
    "WriteRGBDots",
    "ReadRGBDots",
    "build_pixel_row",
    "build_rgb_row",
    # Special functions
    "WriteSpecialFunction",
    "ReadSpecialFunction",
    "parse_general_info",
    # Bulletin
    "WriteBulletin",
    "StopBulletin",
]
