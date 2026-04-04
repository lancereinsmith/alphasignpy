---
icon: lucide/code
---

# Protocol Constants

All constants live in `alphasign.protocol` and are re-exported from `alphasign`.

---

## CommandCode

One-byte command codes (Table 6 of the M-Protocol spec).

| Member | Byte | Description |
|---|---|---|
| `WRITE_TEXT` | `A` | Write TEXT file |
| `READ_TEXT` | `B` | Read TEXT file |
| `WRITE_SPECIAL` | `E` | Write SPECIAL FUNCTION |
| `READ_SPECIAL` | `F` | Read SPECIAL FUNCTION |
| `WRITE_STRING` | `G` | Write STRING file |
| `READ_STRING` | `H` | Read STRING file |
| `WRITE_SMALL_DOTS` | `I` | Write SMALL DOTS picture |
| `READ_SMALL_DOTS` | `J` | Read SMALL DOTS picture |
| `WRITE_RGB_DOTS` | `K` | Write RGB DOTS picture |
| `READ_RGB_DOTS` | `L` | Read RGB DOTS picture |
| `WRITE_LARGE_DOTS` | `M` | Write LARGE DOTS picture |
| `READ_LARGE_DOTS` | `N` | Read LARGE DOTS picture |
| `WRITE_BULLETIN` | `O` | Write AlphaVision Bulletin |

---

## DisplayMode

Text transition / display modes.

| Member | Code | Description |
|---|---|---|
| `ROTATE` | `a` | Right-to-left scroll |
| `HOLD` | `b` | Stationary |
| `FLASH` | `c` | Stationary, flashing |
| `ROLL_UP` | `e` | Previous message pushed up |
| `ROLL_DOWN` | `f` | Previous message pushed down |
| `ROLL_LEFT` | `g` | Previous message pushed left |
| `ROLL_RIGHT` | `h` | Previous message pushed right |
| `WIPE_UP` | `i` | Wipe from bottom to top |
| `WIPE_DOWN` | `j` | Wipe from top to bottom |
| `WIPE_LEFT` | `k` | Wipe from right to left |
| `WIPE_RIGHT` | `l` | Wipe from left to right |
| `SCROLL` | `m` | Push bottom line to top |
| `SPECIAL` | `n` | Special mode (requires `SpecialMode`) |
| `AUTOMODE` | `o` | Automatic mode selection |
| `ROLL_IN` | `p` | Previous pushed toward centre |
| `ROLL_OUT` | `q` | Previous pushed outward |
| `WIPE_IN` | `r` | Wipe inward |
| `WIPE_OUT` | `s` | Wipe outward |
| `COMPRESSED_ROTATE` | `t` | Compressed right-to-left scroll |
| `EXPLODE` | `u` | Flies apart from centre (Alpha 3.0+) |
| `CLOCK` | `v` | Clockwise wipe (Alpha 3.0+) |

---

## SpecialMode

Specifiers for `DisplayMode.SPECIAL`.

| Member | Code | Effect |
|---|---|---|
| `TWINKLE` | `0` | Twinkling |
| `SPARKLE` | `1` | Sparkle over previous |
| `SNOW` | `2` | Snow |
| `INTERLOCK` | `3` | Interlock |
| `SWITCH` | `4` | Alternating character switch |
| `SPRAY` | `5` | Spray right-to-left |
| `STARBURST` | `6` | Starburst explosions |
| `WELCOME` | `7` | Welcome script animation |
| `SLOT_MACHINE` | `8` | Slot machine |
| `NEWS_FLASH` | `9` | Newsflash animation |
| `TRUMPET` | `A` | Trumpet animation |
| `CYCLE_COLORS` | `C` | Colour cycle |
| `THANK_YOU` | `S` | Thank You animation |
| `NO_SMOKING` | `U` | No smoking animation |
| `DONT_DRINK_DRIVE` | `V` | Don't drink and drive |
| `RUNNING_ANIMAL` | `W` | Running animal / fish |
| `FIREWORKS` | `X` | Fireworks |
| `TURBOCAR` | `Y` | Turbo car / balloons |
| `CHERRY_BOMB` | `Z` | Cherry bomb |

---

## DisplayPosition

Vertical/horizontal text position.

| Member | Byte | Description |
|---|---|---|
| `MIDDLE_LINE` | `0x20` | Centred vertically |
| `FILL` | `0x26` | Fill all lines |
| `TOP_LINE` | `0x30` | Top (all lines – 1) |
| `MIDDLE` | `0x31` | Middle (default) |
| `BOTTOM_LINE` | `0x32` | Bottom |
| `LEFT` | `0x3C` | Left (Alpha 3.0+) |
| `RIGHT` | `0x3E` | Right (Alpha 3.0+) |

---

## Color

Embedded colour control sequences.

`RED`, `GREEN`, `AMBER`, `DIM_RED`, `DIM_GREEN`, `BROWN`, `ORANGE`,
`YELLOW`, `RAINBOW1`, `RAINBOW2`, `MIX`, `AUTO`.

---

## PixelColor

Single-character pixel codes for DOTS pictures.

`OFF` (0), `RED` (1), `GREEN` (2), `AMBER` (3), `DIM_RED` (4),
`DIM_GREEN` (5), `BROWN` (6), `ORANGE` (7), `YELLOW` (8).

---

## Font

Font selection control sequences.

`FIVE_HIGH_STD`, `FIVE_STROKE`, `SEVEN_HIGH_STD`, `SEVEN_STROKE`,
`SEVEN_HIGH_FANCY`, `TEN_HIGH_STD`, `SEVEN_SHADOW`, `FULL_HEIGHT_FANCY`,
`FULL_HEIGHT_STD`, `SEVEN_SHADOW_FANCY`, `FIVE_WIDE`, `SEVEN_WIDE`,
`SEVEN_FANCY_WIDE`, `WIDE_STROKE_FIVE`, `FIVE_HIGH_CUSTOM`,
`SEVEN_HIGH_CUSTOM`, `TEN_HIGH_CUSTOM`, `FIFTEEN_HIGH_CUSTOM`.

---

## Other Enums

| Enum | Members |
|---|---|
| `DayOfWeek` | `SUNDAY`–`SATURDAY` |
| `TimeFormat` | `STANDARD` (12h), `MILITARY` (24h) |
| `FileType` | `TEXT`, `STRING`, `DOTS` |
| `FileProtection` | `UNLOCKED`, `LOCKED` |
| `DotsColorDepth` | `MONO`, `THREE_COLOR`, `EIGHT_COLOR` |
| `BulletinPosition` | `TOP`, `BOTTOM` |
| `BulletinJustification` | `LEFT`, `CENTER`, `RIGHT` |
| `SpecialFunction` | All `E`/`F` sub-function codes |
| `TypeCode` | Sign type codes |

---

## Framing Constants

```python
from alphasign.protocol import SYNC, SOH, STX, ETX, EOT, ESC, DELAY, ACK, NAK
```

| Constant | Value | Meaning |
|---|---|---|
| `SYNC` | `b"\x00" × 5` | Sync / baud-rate establishment |
| `SOH` | `b"\x01"` | Start of Header |
| `STX` | `b"\x02"` | Start of Text |
| `ETX` | `b"\x03"` | End of Text |
| `EOT` | `b"\x04"` | End of Transmission |
| `ESC` | `b"\x1B"` | Escape (precedes display position) |
| `DELAY` | `b"\xFF"` | 100 ms timing marker (never transmitted) |
| `ACK` | `0x06` | Acknowledgement (int) |
| `NAK` | `0x15` | Negative acknowledgement (int) |
