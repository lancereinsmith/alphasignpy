---
icon: lucide/file-code-2
---

# Examples

Working examples are in the
[`examples/`][ex] directory.
Each one is a self-contained script you can run directly.

[ex]: https://github.com/lancereinsmith/python-alphasign/tree/main/examples

All examples assume a sign connected via USB serial at
`/dev/ttyUSB0`.
Change the port and `SignType` to match your setup.

## Hello World

Send a message using the priority file
(no memory configuration needed).

```python
from alphasign import Packet, Sign, SignType
from alphasign.commands import WriteText
from alphasign.protocol import DisplayMode

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)

pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(
    b"Hello, World!", label="0", mode=DisplayMode.HOLD,
))
sign.send(pkt)

sign.close()
```

**File:** `examples/hello_world.py`

## Live Clock

Display the sign's internal clock and date.
The sign renders these live -- no polling required.

```python
message = (
    font(Font.SEVEN_HIGH_STD)
    + color(Color.GREEN) + CTRL_TIME
    + CTRL_NEW_LINE
    + color(Color.RED) + date_code("mm/dd/yy")
)
pkt.add(WriteText(message, label="0", mode=DisplayMode.HOLD))
```

**File:** `examples/clock.py`

## Text Formatting

Demonstrates colors, fonts, speed control, flashing text,
wide characters, and multi-line layouts.

```python
message = (
    font(Font.SEVEN_HIGH_STD) + speed(1)
    + color(Color.RED) + b"ALERT "
    + color(Color.AMBER)
    + CTRL_FLASH_ON + b"!!!" + CTRL_FLASH_OFF
    + CTRL_NEW_LINE
    + font(Font.FIVE_HIGH_STD) + speed(3)
    + color(Color.GREEN) + b"System nominal"
    + CTRL_NEW_LINE
    + CTRL_WIDE_ON
    + color(Color.YELLOW) + b"OK"
    + CTRL_WIDE_OFF
)
```

**File:** `examples/text_formatting.py`

## Image Display

Convert any RGB image to the sign's 9-colour palette
and display it using Small Dots.

```python
img = Image("test.png")
pkt.add(WriteSmallDots(
    img.to_bytes(), label="A",
    width=img.width, height=img.height,
))
```

Requires Pillow (`pip install Pillow`).

**File:** `examples/image_display.py`

## Special Functions

Set the clock, configure memory, control the speaker,
and adjust brightness.

```python
send(WriteSpecialFunction.set_time(14, 30))
send(WriteSpecialFunction.set_date(3, 15, 26))
send(WriteSpecialFunction.set_day_of_week(DayOfWeek.SUNDAY))
send(WriteSpecialFunction.set_dimming_register(
    dim_mode=0, brightness_percent=72,
))
send(WriteSpecialFunction.generate_tone(
    tone_type=2, frequency=0x80, duration=5, repeat=1,
))
```

**File:** `examples/special_functions.py`

## Multi-File Slideshow

Configure multiple TEXT files with different transitions
and set a run sequence so the sign cycles through them
automatically.

```python
send(WriteText(
    color(Color.RED) + b"WELCOME",
    label="A", mode=DisplayMode.ROLL_IN,
))
send(WriteText(
    color(Color.GREEN) + b"alphasignpy demo",
    label="B", mode=DisplayMode.WIPE_IN,
))
send(WriteText(
    color(Color.YELLOW) + b"Have a great day!",
    label="C", mode=DisplayMode.EXPLODE,
))
send(WriteSpecialFunction.set_run_sequence("ABC"))
```

**File:** `examples/multi_file_slideshow.py`

## String Variables

Use STRING files as live-updating variables.
Write the layout once with `string_ref()` placeholders,
then update only the STRING data when values change.

```python
layout = (
    color(Color.AMBER) + b"Temp: "
    + color(Color.RED) + string_ref("a")
    + b"  "
    + color(Color.AMBER) + b"Humidity: "
    + color(Color.GREEN) + string_ref("b")
)
send(WriteText(layout, label="A", mode=DisplayMode.HOLD))

# Later, update just the values:
send(WriteString(b"22.5C", label="a"))
send(WriteString(b"45%", label="b"))
```

**File:** `examples/string_variables.py`

## ACK/NAK Error Handling

Demonstrates reliable communication with ACK/NAK error
checking in both strict and non-strict modes.

```python
# Tell the sign to send ACK/NAK responses
send(WriteSpecialFunction.enable_ack_nak(enabled=True))

# Strict: raises TimeoutError, ProtocolError, NAKError
sign.enable_ack_nak(strict=True)

# Non-strict: only raises NAKError, logs timeouts
sign.enable_ack_nak(strict=False)
```

**File:** `examples/ack_nak_error_handling.py`
