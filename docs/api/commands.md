---
icon: lucide/terminal
---

# Commands

All command classes live in `alphasign.commands` (or their sub-modules).
Each class has a `.code` class attribute (the protocol command byte) and
a `.to_bytes()` method that returns the command's data field.

---

## WriteText / ReadText

```python
from alphasign.commands import WriteText, ReadText
```

### `WriteText(message, label, position, mode, special_mode)`

Write a TEXT file to the sign (command `A`).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `message` | `str \| bytes` | — | Message content with optional control codes. |
| `label` | `str` | `"A"` | One-char file label. `"0"` = priority file. |
| `position` | `DisplayPosition` | `FILL` | Vertical display position. |
| `mode` | `DisplayMode` | `ROTATE` | Transition / display mode. |
| `special_mode` | `SpecialMode \| None` | `None` | Required when `mode=SPECIAL`. |

### `ReadText(label)`

Request the sign to return a TEXT file (command `B`).

### `parse_read_text_response(response)` → `(label, position, mode, message)`

Parse the raw bytes returned by the sign.

---

## WriteString / ReadString

```python
from alphasign.commands import WriteString, ReadString
```

### `WriteString(data, label)`

Write a STRING variable file (command `G`). Max 125 bytes.

STRING files can be embedded in TEXT messages using `string_ref("label")`.
They update without re-sending the parent TEXT file.

### `ReadString(label)`

Request a STRING file (command `H`).

### `parse_read_string_response(response)` → `(label, data)`

---

## Dots Commands

```python
from alphasign.commands import (
    WriteSmallDots, ReadSmallDots,
    WriteLargeDots, ReadLargeDots,
    WriteRGBDots, ReadRGBDots,
    build_pixel_row, build_rgb_row,
)
```

### `WriteSmallDots(pixel_data, label, width, height, compress)`

Write a SMALL DOTS picture (command `I`). Max 255×31 pixels.

Each pixel is one ASCII character from `PixelColor` (e.g. `b"1"` = red).
Rows are terminated with `b"\r"`.

Use `alphasign.Image` to convert a real image to pixel data automatically.

### `WriteLargeDots(pixel_data, label, width, height, compress)`

Write a LARGE DOTS picture (command `M`). Max 65535×65535 pixels.
Same pixel format as SMALL DOTS.

### `WriteRGBDots(pixel_data, label, width, height, compress)`

Write an RGB DOTS picture (command `K`). **Alpha 3.0 / AlphaEclipse 3600 only.**

Each pixel is 6 ASCII hex chars: `RRGGBB`. Rows terminated with `b"\r"`.

### `build_pixel_row(pixels)` → `bytes`

Build one row of DOTS data from a list of `PixelColor` values.

```python
from alphasign.commands import build_pixel_row
from alphasign.protocol import PixelColor

row = build_pixel_row([PixelColor.RED, PixelColor.OFF, PixelColor.GREEN])
# b"102\r"
```

### `build_rgb_row(pixels)` → `bytes`

Build one row of RGB data from a list of `(R, G, B)` tuples.

```python
row = build_rgb_row([(255, 0, 0), (0, 255, 0)])
# b"FF000000FF00\r"
```

---

## WriteSpecialFunction

```python
from alphasign.commands import WriteSpecialFunction
```

All special functions are **factory class methods** — do not instantiate directly.

### Time & Date

```python
WriteSpecialFunction.set_time(hours, minutes)
WriteSpecialFunction.set_date(month, day, year)
WriteSpecialFunction.set_day_of_week(DayOfWeek.MONDAY)
WriteSpecialFunction.set_time_format(TimeFormat.MILITARY)
```

### Audio

```python
WriteSpecialFunction.set_speaker(enabled=True)
WriteSpecialFunction.generate_tone(tone_type=1)
WriteSpecialFunction.generate_tone(tone_type=2, frequency=0x20, duration=5, repeat=2)
```

### Memory

```python
WriteSpecialFunction.clear_memory()
WriteSpecialFunction.configure_memory([
    {"label": "A", "type": FileType.TEXT, "size": 256},
    {"label": "B", "type": FileType.STRING, "size": 64},
    {"label": "P", "type": FileType.DOTS, "size": (16, 60),
     "color_depth": DotsColorDepth.EIGHT_COLOR},
])
WriteSpecialFunction.configure_large_dots_memory([...], append=False)
```

### Display Scheduling

```python
WriteSpecialFunction.set_run_time_table("A", start_time=0x30, stop_time=0x60)
WriteSpecialFunction.set_run_sequence("KABAC")
WriteSpecialFunction.set_run_day_table("A", start_day=0x02, stop_day=0x06)
```

### Dimming

```python
WriteSpecialFunction.set_dimming_register(dim_mode=0, brightness_percent=72)
WriteSpecialFunction.set_dimming_times(start_code=0x30, stop_code=0x60)
```

### XY Position

```python
WriteSpecialFunction.display_at_xy(x=10, y=2, text="HELLO", enabled=True)
```

### Hardware

```python
WriteSpecialFunction.soft_reset()
WriteSpecialFunction.set_serial_address("0A")
WriteSpecialFunction.clear_error_status()
```

### ACK/NAK

```python
WriteSpecialFunction.enable_ack_nak(True)   # enable on sign
WriteSpecialFunction.enable_ack_nak(False)  # disable on sign
```

### Counter

```python
WriteSpecialFunction.set_counter([
    {
        "control": 0x80,     # counter on, increment
        "start_value": 0,
        "change_value": 1,
        "current_value": 0,
        "target_value": 100,
        "change_minutes": 0,
        "change_hours": 1,
    }
])
```

---

## ReadSpecialFunction

```python
from alphasign.commands import ReadSpecialFunction
from alphasign.protocol import SpecialFunction

cmd = ReadSpecialFunction(SpecialFunction.SET_TIME)
```

Sends a read request (command `F`). Call `sign.read_response()` after
`sign.send()` to receive the data.

Available functions to read: all `SpecialFunction` enum members.

### `parse_general_info(response)` → `dict`

Parse a `F"` (General Info) response. Returns a dict with keys:
`firmware`, `firmware_rev`, `date`, `time`, `time_format`, `speaker`,
`memory_pool`, `memory_free`.

---

## WriteBulletin / StopBulletin

```python
from alphasign.commands import WriteBulletin, StopBulletin
from alphasign.protocol import BulletinPosition, BulletinJustification

pkt.add(WriteBulletin(
    "SALE 50% OFF",
    position=BulletinPosition.TOP,
    justification=BulletinJustification.CENTER,
    count=3,
))

# Stop a running bulletin
pkt.add(StopBulletin())
```

AlphaVision signs only (command `O` / `OT`). Max 225 characters.
