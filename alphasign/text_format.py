"""Text formatting helpers.

This module provides builder functions and control-code constants for
constructing Alpha Sign message strings with embedded colours, fonts,
animations, and other effects.

Control codes are always returned as ``bytes`` so they can be concatenated
directly with ``b"..."`` string literals or passed to :class:`WriteText`.

Example::

    from alphasign.text_format import color, font, speed, date_code
    from alphasign.protocol import Color, Font

    message = (
        color(Color.RED)
        + b"Temp: "
        + color(Color.YELLOW)
        + b"22.5"
        + b"\\xB0C"
        + speed(3)
    )
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Display mode / special mode are in protocol.py — re-export here for convenience
# ---------------------------------------------------------------------------
from .protocol import Color, DayOfWeek, DisplayMode, Font, SpecialMode  # noqa: F401

# ---------------------------------------------------------------------------
# Basic control sequences (no enum needed)
# ---------------------------------------------------------------------------

# Character-level toggles
CTRL_DOUBLE_HIGH_ON = b"\x051"
CTRL_DOUBLE_HIGH_OFF = b"\x050"
CTRL_TRUE_DESC_ON = b"\x061"
CTRL_TRUE_DESC_OFF = b"\x060"
CTRL_FLASH_ON = b"\x071"
CTRL_FLASH_OFF = b"\x070"
CTRL_NO_HOLD_SPEED = b"\x09"
CTRL_NEW_PAGE = b"\x0c"
CTRL_NEW_LINE = b"\x0d"
CTRL_WIDE_OFF = b"\x11"
CTRL_WIDE_ON = b"\x12"
CTRL_TIME = b"\x13"  # Insert current time
CTRL_SPACE_PROP = b"\x1e0"  # Proportional spacing (default)
CTRL_SPACE_FIXED = b"\x1e1"  # Fixed-width spacing


# ---------------------------------------------------------------------------
# Builder functions
# ---------------------------------------------------------------------------


def color(c: Color) -> bytes:
    """Return the control code sequence to switch to colour *c*.

    Args:
        c: A :class:`~alphasign.protocol.Color` enum member.

    Returns:
        2-3 byte control sequence to embed in a message.

    Example::

        msg = color(Color.RED) + b"ALERT" + color(Color.GREEN) + b" OK"
    """
    return c.value


def rgb_color(r: int, g: int, b_val: int, *, shade: bool = False) -> bytes:
    """Return a 24-bit RGB colour control sequence (Alpha 3.0+ only).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b_val: Blue channel (0-255).
        shade: If ``True``, use the *shade* variant (``Y`` prefix instead of ``Z``).

    Returns:
        9-byte control sequence.
    """
    prefix = b"Y" if shade else b"Z"
    return b"\x1c" + prefix + f"{r:02X}{g:02X}{b_val:02X}".encode()


def font(f: Font) -> bytes:
    """Return the control code sequence to switch to font *f*.

    Args:
        f: A :class:`~alphasign.protocol.Font` enum member.

    Example::

        msg = font(Font.SEVEN_HIGH_STD) + b"Big text"
    """
    return f.value


def speed(level: int) -> bytes:
    """Return the speed control code for *level* (1-5).

    Args:
        level: Display speed where 1 is slowest and 5 is fastest.

    Raises:
        ValueError: If *level* is not in 1-5.
    """
    if not 1 <= level <= 5:
        raise ValueError(f"Speed level must be 1-5, got {level}.")
    return bytes([0x14 + level])  # 0x15-0x19


def speed_control(level: int) -> bytes:
    """Return an Alpha 2.0 *speed control* code for *level* (1-5).

    This is different from :func:`speed` — it uses the ``0x09`` prefix.

    Args:
        level: Speed level (1-5).
    """
    if not 1 <= level <= 5:
        raise ValueError(f"Speed level must be 1-5, got {level}.")
    return b"\x09" + str(level).encode()


def attr(name: str, enabled: bool) -> bytes:
    """Return a character attribute toggle control code.

    Valid attribute names:

    * ``"wide"`` — Wide characters.
    * ``"dwide"`` — Double-wide characters.
    * ``"dhigh"`` — Double-high characters.
    * ``"td"`` — True descenders.
    * ``"fw"`` — Fixed-width characters.
    * ``"fancy"`` — Fancy characters.
    * ``"aux"`` — Auxiliary port.
    * ``"shadow"`` — Shadow characters.

    Args:
        name: Attribute name (case-sensitive).
        enabled: ``True`` to enable, ``False`` to disable.

    Raises:
        ValueError: If *name* is not recognised.
    """
    attrs = {
        "wide": b"\x1d0",
        "dwide": b"\x1d1",
        "dhigh": b"\x1d2",
        "td": b"\x1d3",
        "fw": b"\x1d4",
        "fancy": b"\x1d5",
        "aux": b"\x1d6",
        "shadow": b"\x1d7",
    }
    code = attrs.get(name)
    if code is None:
        raise ValueError(f"Unknown attribute {name!r}. Valid names: {', '.join(attrs)}.")
    return code + (b"1" if enabled else b"0")


def temperature(unit: str = "c") -> bytes:
    """Return the temperature display control code.

    Args:
        unit: ``"c"`` for Celsius, ``"f"`` for Fahrenheit.

    Returns:
        2-byte control code sequence.
    """
    mapping = {"c": b"\x08\x1c", "f": b"\x08\x1d"}
    code = mapping.get(unit.lower())
    if code is None:
        raise ValueError(f"Unit must be 'c' or 'f', got {unit!r}.")
    return code


def date_code(fmt: str = "mm/dd/yy") -> bytes:
    """Return the date display control code for the given format string.

    Valid format strings:

    ``"mm/dd/yy"``, ``"dd/mm/yy"``, ``"mm-dd-yy"``, ``"dd-mm-yy"``,
    ``"mm.dd.yy"``, ``"dd.mm.yy"``, ``"mm dd yy"``, ``"dd mm yy"``,
    ``"mmm.dd.yyyy"``, ``"dow"``

    Args:
        fmt: Date format identifier.

    Raises:
        ValueError: If *fmt* is not recognised.
    """
    formats = {
        "mm/dd/yy": b"\x0b0",
        "dd/mm/yy": b"\x0b1",
        "mm-dd-yy": b"\x0b2",
        "dd-mm-yy": b"\x0b3",
        "mm.dd.yy": b"\x0b4",
        "dd.mm.yy": b"\x0b5",
        "mm dd yy": b"\x0b6",
        "dd mm yy": b"\x0b7",
        "mmm.dd.yyyy": b"\x0b8",
        "dow": b"\x0b9",
    }
    code = formats.get(fmt)
    if code is None:
        raise ValueError(f"Unknown date format {fmt!r}. Valid formats: {', '.join(formats)}.")
    return code


def string_ref(label: str) -> bytes:
    """Return the control code to embed a STRING variable file in a message.

    Args:
        label: The one-character STRING file label.

    Returns:
        2-byte control sequence (``0x10`` + label).
    """
    if len(label) != 1:
        raise ValueError("STRING label must be exactly one character.")
    return b"\x10" + label.encode()


def picture_ref(label: str) -> bytes:
    """Return the control code to embed a DOTS picture in a message.

    Args:
        label: The one-character picture file label.

    Returns:
        2-byte control sequence (``0x14`` + label).
    """
    if len(label) != 1 or not label.isalnum():
        raise ValueError("Picture label must be exactly one alphanumeric character.")
    return b"\x14" + label.upper().encode()


def counter_ref(index: int) -> bytes:
    """Return the control code to display the value of counter *index*.

    Args:
        index: Counter number (1-5).

    Raises:
        ValueError: If *index* is not in 1-5.
    """
    if not 1 <= index <= 5:
        raise ValueError(f"Counter index must be 1-5, got {index}.")
    return b"\x08" + bytes([0x79 + index])  # 0x7A-0x7E


def animation(
    anim_type: str,
    filename: str,
    hold_time: int = 0,
) -> bytes:
    """Return the control code to play a Quick Flick or DOTS PICTURE animation.

    Args:
        anim_type: ``"quick"`` (Quick Flick), ``"faster"`` (Faster Flicks,
            Alpha 3.0+), or ``"dots"`` (DOTS PICTURE file).
        filename: Up to 9-character filename (padded with leading spaces).
        hold_time: Hold/display time.  For ``"quick"`` and ``"dots"``:
            tenths of a second.  For ``"faster"``: hundredths of a second.

    Raises:
        ValueError: If *anim_type* is unrecognised.
    """
    types = {"quick": b"C", "faster": b"G", "dots": b"L"}
    code = types.get(anim_type)
    if code is None:
        raise ValueError(f"Unknown animation type {anim_type!r}. Valid types: {', '.join(types)}.")
    fname = (" " * (9 - len(filename)) + filename[:9]).encode()
    return b"\x1f" + code + fname + f"{hold_time:04X}".encode()
