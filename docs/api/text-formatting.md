---
icon: lucide/type
---

# Text Formatting

The `alphasign.text_format` module provides builder functions that return
embedded control-code bytes for Alpha sign messages.

All functions return `bytes` and can be concatenated directly:

```python
from alphasign.text_format import color, font, speed
from alphasign.protocol import Color, Font

msg = color(Color.RED) + font(Font.SEVEN_HIGH_STD) + b"Hello!"
```

---

## Colours

### `color(c)` → `bytes`

Switch to a named colour.

```python
from alphasign.protocol import Color

color(Color.RED)       # b"\x1C1"
color(Color.GREEN)     # b"\x1C2"
color(Color.AMBER)     # b"\x1C3"
color(Color.DIM_RED)   # b"\x1C4"
color(Color.DIM_GREEN) # b"\x1C5"
color(Color.BROWN)     # b"\x1C6"
color(Color.ORANGE)    # b"\x1C7"
color(Color.YELLOW)    # b"\x1C8"
color(Color.RAINBOW1)  # b"\x1C9"
color(Color.RAINBOW2)  # b"\x1CA"
color(Color.MIX)       # b"\x1CB"
color(Color.AUTO)      # b"\x1CC"
```

### `rgb_color(r, g, b, *, shade=False)` → `bytes`

24-bit RGB colour (Alpha 3.0+ only).

```python
rgb_color(255, 128, 0)            # orange
rgb_color(0, 200, 255, shade=True)  # tinted blue
```

---

## Fonts

### `font(f)` → `bytes`

Switch to a named font.

```python
from alphasign.protocol import Font

font(Font.FIVE_HIGH_STD)      # b"\x1A1"
font(Font.SEVEN_HIGH_STD)     # b"\x1A3"  (default)
font(Font.TEN_HIGH_STD)       # b"\x1A6"
font(Font.FULL_HEIGHT_STD)    # b"\x1A9"
font(Font.SEVEN_HIGH_CUSTOM)  # b"\x1AX"
```

Full list in `alphasign.protocol.Font`.

---

## Speed

### `speed(level)` → `bytes`

Set display speed (1 = slowest, 5 = fastest).

```python
speed(1)  # b"\x15"
speed(3)  # b"\x17"
speed(5)  # b"\x19"
```

### `speed_control(level)` → `bytes`

Alpha 2.0 speed control variant (uses `0x09` prefix).

---

## Character Attributes

### `attr(name, enabled)` → `bytes`

Toggle a character attribute.

| Name | Effect |
|---|---|
| `"wide"` | Wide characters |
| `"dwide"` | Double-wide |
| `"dhigh"` | Double-high |
| `"td"` | True descenders |
| `"fw"` | Fixed-width |
| `"fancy"` | Fancy style |
| `"aux"` | Auxiliary port |
| `"shadow"` | Shadow characters |

```python
attr("wide", True)   # b"\x1D01"
attr("wide", False)  # b"\x1D00"
```

---

## Date & Time

### `date_code(fmt)` → `bytes`

Insert a live date in the specified format.

| Format string | Example |
|---|---|
| `"mm/dd/yy"` | 12/25/24 |
| `"dd/mm/yy"` | 25/12/24 |
| `"mmm.dd.yyyy"` | Dec.25.2024 |
| `"dow"` | Wednesday |

### `CTRL_TIME`

Constant (`b"\x13"`) — insert the current time.

```python
from alphasign.text_format import CTRL_TIME, date_code

msg = b"Date: " + date_code("dd/mm/yy") + b"  Time: " + CTRL_TIME
```

---

## Temperature

### `temperature(unit)` → `bytes`

Insert the current temperature reading (Solar series signs only).

```python
temperature("c")  # Celsius
temperature("f")  # Fahrenheit
```

---

## Variable References

### `string_ref(label)` → `bytes`

Embed a STRING file value in a TEXT message.

```python
# In the TEXT message:
msg = b"Temp: " + string_ref("B") + b" degrees"
# Update the value live:
pkt.add(WriteString("22.5", label="B"))
```

### `picture_ref(label)` → `bytes`

Embed a DOTS picture inline.

### `counter_ref(index)` → `bytes`

Display a hardware counter value (counters 1–5).

---

## Animations

### `animation(anim_type, filename, hold_time)` → `bytes`

Reference a Quick Flick, Faster Flicks, or DOTS PICTURE animation.

| `anim_type` | Description |
|---|---|
| `"quick"` | Quick Flick animation |
| `"faster"` | Faster Flicks (Alpha 3.0+) |
| `"dots"` | DOTS PICTURE file |

```python
animation("dots", "LOGO", hold_time=10)  # show LOGO for 1.0 s
```

---

## Control Code Constants

| Constant | Value | Effect |
|---|---|---|
| `CTRL_FLASH_ON` | `b"\x071"` | Start flashing |
| `CTRL_FLASH_OFF` | `b"\x070"` | Stop flashing |
| `CTRL_NEW_LINE` | `b"\x0D"` | New line |
| `CTRL_NEW_PAGE` | `b"\x0C"` | New page |
| `CTRL_TIME` | `b"\x13"` | Current time |
| `CTRL_WIDE_ON` | `b"\x12"` | Wide chars on |
| `CTRL_WIDE_OFF` | `b"\x11"` | Wide chars off |
| `CTRL_SPACE_PROP` | `b"\x1E0"` | Proportional spacing |
| `CTRL_SPACE_FIXED` | `b"\x1E1"` | Fixed-width spacing |
| `CTRL_DOUBLE_HIGH_ON` | `b"\x051"` | Double-high on |
| `CTRL_NO_HOLD_SPEED` | `b"\x09"` | No-hold speed |
