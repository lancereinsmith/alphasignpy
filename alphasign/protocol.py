"""Alpha Sign Communications Protocol constants.

All byte values are defined here as enums or module-level constants.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Framing bytes
# ---------------------------------------------------------------------------

SYNC = b"\x00\x00\x00\x00\x00"  # 5 NUL bytes — establishes baud rate
SOH = b"\x01"  # Start Of Header
STX = b"\x02"  # Start of TeXt
ETX = b"\x03"  # End of TeXt (precedes checksum)
EOT = b"\x04"  # End Of Transmission
ESC = b"\x1b"  # Escape (precedes display position in TEXT)

# Response bytes (ACK/NAK from sign)
ACK = 0x06
NAK = 0x15

# Timing marker — causes a 100 ms pause during send(); never transmitted
DELAY = b"\xff"

# Addressing
BROADCAST_ADDRESS = "00"
WILDCARD_ADDRESS = "??"
PRIORITY_FILE_LABEL = "0"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CommandCode(Enum):
    """One-byte command codes (Table 6 of the protocol spec)."""

    WRITE_TEXT = b"A"
    READ_TEXT = b"B"
    WRITE_SPECIAL = b"E"
    READ_SPECIAL = b"F"
    WRITE_STRING = b"G"
    READ_STRING = b"H"
    WRITE_SMALL_DOTS = b"I"
    READ_SMALL_DOTS = b"J"
    WRITE_RGB_DOTS = b"K"
    READ_RGB_DOTS = b"L"
    WRITE_LARGE_DOTS = b"M"
    READ_LARGE_DOTS = b"N"
    WRITE_BULLETIN = b"O"


class TypeCode(Enum):
    """Sign type codes used in the packet header."""

    ALL = b"Z"
    SERIAL_CLOCK = b"!"
    ALPHAVISION = b"#"
    FULL_MATRIX_ALPHAVISION = b"$"
    SIGN_215R = b"e"
    SIGN_215C = b"f"
    SIGN_4120R = b"g"
    SIGN_4160R = b"h"
    SIGN_4200R = b"i"
    SIGN_4240R = b"j"
    SIGN_4200C = b"c"
    SIGN_4240C = b"c"
    SIGN_300 = b"k"
    RESPONSE = b"0"
    ONE_LINE = b"1"
    TWO_LINE = b"2"


class DisplayMode(Enum):
    """Text display / transition modes.

    Use ``DisplayMode.SPECIAL`` together with ``SpecialMode`` for special effects.
    """

    ROTATE = b"a"
    HOLD = b"b"
    FLASH = b"c"
    ROLL_UP = b"e"
    ROLL_DOWN = b"f"
    ROLL_LEFT = b"g"
    ROLL_RIGHT = b"h"
    WIPE_UP = b"i"
    WIPE_DOWN = b"j"
    WIPE_LEFT = b"k"
    WIPE_RIGHT = b"l"
    SCROLL = b"m"
    SPECIAL = b"n"
    AUTOMODE = b"o"
    ROLL_IN = b"p"
    ROLL_OUT = b"q"
    WIPE_IN = b"r"
    WIPE_OUT = b"s"
    COMPRESSED_ROTATE = b"t"
    EXPLODE = b"u"  # Alpha 3.0+
    CLOCK = b"v"  # Alpha 3.0+


class SpecialMode(Enum):
    """Specifier byte used when ``DisplayMode`` is ``SPECIAL`` (mode code 'n')."""

    TWINKLE = b"0"
    SPARKLE = b"1"
    SNOW = b"2"
    INTERLOCK = b"3"
    SWITCH = b"4"
    SPRAY = b"5"
    STARBURST = b"6"
    WELCOME = b"7"
    SLOT_MACHINE = b"8"
    NEWS_FLASH = b"9"
    TRUMPET = b"A"
    CYCLE_COLORS = b"C"
    THANK_YOU = b"S"
    NO_SMOKING = b"U"
    DONT_DRINK_DRIVE = b"V"
    RUNNING_ANIMAL = b"W"
    FIREWORKS = b"X"
    TURBOCAR = b"Y"
    CHERRY_BOMB = b"Z"


class DisplayPosition(Enum):
    """Vertical/horizontal display position inside the text area."""

    MIDDLE_LINE = b" "  # 20H centred vertically
    FILL = b"&"  # 26H fill all lines, centred
    TOP_LINE = b"0"  # 30H uses all lines minus 1
    MIDDLE = b"1"  # 31H middle (default)
    BOTTOM_LINE = b"2"  # 32H bottom line
    LEFT = b"<"  # 3CH Alpha 3.0+
    RIGHT = b">"  # 3EH Alpha 3.0+


class Color(Enum):
    """Embedded color control sequences for text messages.

    Prepend ``color.value`` directly into the ASCII message string.
    """

    RED = b"\x1c1"
    GREEN = b"\x1c2"
    AMBER = b"\x1c3"
    DIM_RED = b"\x1c4"
    DIM_GREEN = b"\x1c5"
    BROWN = b"\x1c6"
    ORANGE = b"\x1c7"
    YELLOW = b"\x1c8"
    RAINBOW1 = b"\x1c9"
    RAINBOW2 = b"\x1cA"
    MIX = b"\x1cB"
    AUTO = b"\x1cC"


class PixelColor(Enum):
    """Single-character pixel color codes used in DOTS picture data."""

    OFF = b"0"
    RED = b"1"
    GREEN = b"2"
    AMBER = b"3"
    DIM_RED = b"4"
    DIM_GREEN = b"5"
    BROWN = b"6"
    ORANGE = b"7"
    YELLOW = b"8"


class Font(Enum):
    """Font selection control sequences (1AH + specifier)."""

    FIVE_HIGH_STD = b"\x1a1"
    FIVE_STROKE = b"\x1a2"
    SEVEN_HIGH_STD = b"\x1a3"
    SEVEN_STROKE = b"\x1a4"
    SEVEN_HIGH_FANCY = b"\x1a5"
    TEN_HIGH_STD = b"\x1a6"
    SEVEN_SHADOW = b"\x1a7"
    FULL_HEIGHT_FANCY = b"\x1a8"
    FULL_HEIGHT_STD = b"\x1a9"
    SEVEN_SHADOW_FANCY = b"\x1a:"
    FIVE_WIDE = b"\x1a;"
    SEVEN_WIDE = b"\x1a<"
    SEVEN_FANCY_WIDE = b"\x1a="
    WIDE_STROKE_FIVE = b"\x1a>"
    FIVE_HIGH_CUSTOM = b"\x1aW"
    SEVEN_HIGH_CUSTOM = b"\x1aX"
    TEN_HIGH_CUSTOM = b"\x1aY"
    FIFTEEN_HIGH_CUSTOM = b"\x1aZ"


class DayOfWeek(Enum):
    """Day-of-week values for the ``set_day_of_week`` special function."""

    SUNDAY = b"1"
    MONDAY = b"2"
    TUESDAY = b"3"
    WEDNESDAY = b"4"
    THURSDAY = b"5"
    FRIDAY = b"6"
    SATURDAY = b"7"


class TimeFormat(Enum):
    """Time display format for ``set_time_format``."""

    STANDARD = b"S"  # 12-hour with am/pm
    MILITARY = b"M"  # 24-hour


class FileType(Enum):
    """File types used in memory configuration."""

    TEXT = b"A"
    STRING = b"B"
    DOTS = b"D"


class FileProtection(Enum):
    """IR keyboard / remote protection for memory configuration."""

    UNLOCKED = b"U"
    LOCKED = b"L"


class DotsColorDepth(Enum):
    """Color depth specifier in SMALL DOTS memory configuration."""

    MONO = b"1000"
    THREE_COLOR = b"2000"
    EIGHT_COLOR = b"4000"


class BulletinPosition(Enum):
    """Vertical position for AlphaVision bulletin messages."""

    TOP = b"T"
    BOTTOM = b"B"


class BulletinJustification(Enum):
    """Horizontal justification for AlphaVision bulletin messages."""

    LEFT = b"L"
    CENTER = b"C"
    RIGHT = b"R"


class SpecialFunction(Enum):
    """Function label bytes for the Write/Read Special Function commands (E/F)."""

    SET_TIME = b" "  # 20H — set time of day
    SPEAKER = b"!"  # 21H — enable/disable speaker
    GENERAL_INFO = b'"'  # 22H — read general info (read only)
    MEMORY_POOL = b"#"  # 23H — read memory pool size (read only)
    MEMORY_CONFIG = b"$"  # 24H — set/read memory configuration
    MEMORY_DUMP = b"%"  # 25H — read memory dump (read only)
    DAY_OF_WEEK = b"&"  # 26H — set/read day of week
    TIME_FORMAT = b"'"  # 27H — set/read time format
    TONE = b"("  # 28H — generate tone
    RUN_TIME_TABLE = b")"  # 29H — set/read run time table
    SERIAL_ERROR_STATUS = b"*"  # 2AH — read serial error status (read only)
    XY_POSITION = b"+"  # 2BH — display text at X/Y position
    SOFT_RESET = b","  # 2CH — soft reset
    NETWORK_QUERY = b"-"  # 2DH — network query (read only)
    RUN_SEQUENCE = b"."  # 2EH — set/read run sequence
    DIMMING_REG = b"/"  # 2FH — set dimming register
    DIMMING_TIMES = b"0"  # 30H — set dimming times
    RUN_DAY_TABLE = b"2"  # 32H — set/read run day table
    CLEAR_ERROR = b"4"  # 34H — clear error status
    SET_COUNTER = b"5"  # 35H — set counter
    SERIAL_ADDRESS = b"7"  # 37H — set/read serial address
    LARGE_DOTS_CONFIG = b"8"  # 38H — set LARGE DOTS memory config
    APPEND_LARGE_DOTS = b"9"  # 39H — append LARGE DOTS config
    RUN_FILE_TIMES = b":"  # 3AH — set run file times (Alpha 2.0+)
    SET_DATE = b";"  # 3BH — set date
    CUSTOM_CHARSET = b"<"  # 3CH — program custom charset (Alpha 2.0+)
    AUTOMODE_TABLE = b">"  # 3EH — set automode table (Alpha 2.0+)
    DIMMING_CONTROL = b"@"  # 40H — set dimming control register (Alpha 2.0+)
    COLOR_CORRECTION = b"C"  # 43H — set color correction
    ACK_NAK = b"s"  # 73H — enable/disable ACK/NAK responses


class SerialErrorStatus:
    """Bit masks for the Serial Error Status Register (returned with ACK/NAK)."""

    ILLEGAL_COMMAND = 0x20  # Bit 5 — illegal command code or file label
    CHECKSUM_ERROR = 0x10  # Bit 4 — checksum error in received packet
    BUFFER_OVERFLOW = 0x08  # Bit 3 — insufficient serial buffer
    SERIAL_TIMEOUT = 0x04  # Bit 2 — serial timeout
    BIT_FRAMING = 0x02  # Bit 1 — bit framing error
    PARITY = 0x01  # Bit 0 — parity error
    DEFAULT = 0x40  # Default value (bit 6 always 1)
