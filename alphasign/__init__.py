"""alphasignpy — Python library for Alpha Sign LED displays.

Implements the Alpha Sign Communications Protocol (M-Protocol) for
controlling Alpha, BetaBrite, and compatible LED signs over serial.

Quick start::

    from alphasign import Sign, Packet, SignType
    from alphasign.commands import WriteText, WriteSpecialFunction
    from alphasign.protocol import DisplayMode, Color

    sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
    sign.open("/dev/ttyUSB0", dtr=False)

    # Configure memory (required for labelled files; not for priority "0")
    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(WriteSpecialFunction.configure_memory([
        {"label": "A", "type": FileType.TEXT, "size": 256},
    ]))
    sign.send(pkt)

    # Send a text message
    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(WriteText(b"Hello, world!", mode=DisplayMode.ROTATE))
    sign.send(pkt)

    sign.close()

Original author: jason@prototux.net (prototux)
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from .commands import (
    ReadLargeDots,
    ReadRGBDots,
    ReadSmallDots,
    ReadSpecialFunction,
    ReadString,
    ReadText,
    StopBulletin,
    WriteBulletin,
    WriteLargeDots,
    WriteRGBDots,
    WriteSmallDots,
    WriteSpecialFunction,
    WriteString,
    WriteText,
    build_pixel_row,
    build_rgb_row,
    parse_general_info,
    parse_read_text_response,
)
from .exceptions import (
    AlphaSignError,
    ChecksumError,
    ConnectionError,
    InvalidParameterError,
    NAKError,
    PacketError,
    ProtocolError,
    TimeoutError,
)
from .image import Image
from .packet import Packet
from .protocol import (
    Color,
    CommandCode,
    DayOfWeek,
    DisplayMode,
    DisplayPosition,
    DotsColorDepth,
    FileProtection,
    FileType,
    Font,
    PixelColor,
    SpecialFunction,
    SpecialMode,
    TimeFormat,
    TypeCode,
)
from .sign import Sign
from .sign_types import SignDefinition, SignType
from .text_format import (
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

try:
    __version__ = _version("alphasignpy")
except PackageNotFoundError:
    __version__ = "unknown"
__author__ = "Lance Reinsmith"
__original_author__ = "jason@prototux.net (prototux)"
__license__ = "MIT"

__all__ = [  # noqa: RUF022
    # Sign & packet
    "Sign",
    "Packet",
    "SignType",
    "SignDefinition",
    # Commands — text
    "WriteText",
    "ReadText",
    "parse_read_text_response",
    # Commands — string
    "WriteString",
    "ReadString",
    # Commands — dots
    "WriteSmallDots",
    "ReadSmallDots",
    "WriteLargeDots",
    "ReadLargeDots",
    "WriteRGBDots",
    "ReadRGBDots",
    "build_pixel_row",
    "build_rgb_row",
    # Commands — special functions
    "WriteSpecialFunction",
    "ReadSpecialFunction",
    "parse_general_info",
    # Commands — bulletin
    "WriteBulletin",
    "StopBulletin",
    # Protocol constants
    "Color",
    "CommandCode",
    "DayOfWeek",
    "DisplayMode",
    "DisplayPosition",
    "DotsColorDepth",
    "FileProtection",
    "FileType",
    "Font",
    "PixelColor",
    "SpecialFunction",
    "SpecialMode",
    "TimeFormat",
    "TypeCode",
    # Text formatting
    "color",
    "rgb_color",
    "font",
    "speed",
    "speed_control",
    "attr",
    "temperature",
    "date_code",
    "string_ref",
    "picture_ref",
    "counter_ref",
    "animation",
    "CTRL_FLASH_ON",
    "CTRL_FLASH_OFF",
    "CTRL_NEW_LINE",
    "CTRL_NEW_PAGE",
    "CTRL_TIME",
    "CTRL_WIDE_ON",
    "CTRL_WIDE_OFF",
    # Image
    "Image",
    # Exceptions
    "AlphaSignError",
    "ConnectionError",
    "PacketError",
    "ChecksumError",
    "ProtocolError",
    "NAKError",
    "TimeoutError",
    "InvalidParameterError",
]
