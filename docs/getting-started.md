---
icon: lucide/rocket
---

# Getting Started

## Installation

```bash
pip install alphasignpy
```

For development (includes linting, type checking, tests, docs):

```bash
pip install "alphasignpy[dev]"
```

---

## Hardware Setup

Connect your Alpha sign to your computer via:

- **RS-232 serial cable** directly to a COM port, or
- **USB-to-serial adapter** (creates `/dev/ttyUSB0` on Linux, `COM3` etc. on Windows).

The protocol uses **7E1 framing**: 7 data bits, even parity, 1 stop bit, 9600 baud.
This is handled automatically by `sign.open()`.

### DTR

Many USB-to-serial adapters assert DTR on open, which can accidentally reset some
signs. Pass `dtr=False` (the default) to suppress this:

```python
sign.open("/dev/ttyUSB0", dtr=False)
```

---

## The Sign Object

```python
from alphasign import Sign, SignType

sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
sign.open("/dev/ttyUSB0")
```

`Sign` is a **singleton** — calling `Sign(...)` always returns the same instance.
This matches the typical use case of one sign per process.

Available sign types:

| `SignType` attribute | Model | Width | Height |
|---|---|---|---|
| `ALL` | Generic / broadcast | 255 | 255 |
| `ALPHA_2X0C` | Alpha 210C / 220C | 60 | 7 |
| `ALPHA_4200C` | Alpha 4200C / 4240C | 200 | 16 |
| `ALPHA_3600` | AlphaEclipse 3600 (RGB) | 200 | 16 |

Use **broadcast address `"00"`** to send to all signs on the network.

---

## Sending Messages

All commands are wrapped in a `Packet` and sent via `sign.send()`:

```python
from alphasign import Packet
from alphasign.commands import WriteText
from alphasign.protocol import DisplayMode

pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(b"Hello!", mode=DisplayMode.HOLD))
sign.send(pkt)
```

### Priority Text File

The **priority file** (label `"0"`) always exists — no memory configuration
needed. It immediately overrides all other files:

```python
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(b"URGENT: check back later", label="0"))
sign.send(pkt)

# Clear priority file by sending empty message
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(b"", label="0"))
sign.send(pkt)
```

---

## Memory Configuration

Most files (other than priority `"0"`) must be configured in memory before use.
Use `WriteSpecialFunction.configure_memory()`:

```python
from alphasign.commands import WriteSpecialFunction
from alphasign.protocol import FileType, FileProtection

pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.configure_memory([
    {
        "label": "A",
        "type": FileType.TEXT,
        "protection": FileProtection.UNLOCKED,
        "size": 256,
    },
    {
        "label": "B",
        "type": FileType.STRING,
        "size": 64,
    },
]))
sign.send(pkt)
```

!!! warning
    `configure_memory()` **erases** existing files. Only call it when setting
    up a new sign or changing the file layout.

---

## Text Formatting

Use the `text_format` module to build messages with embedded effects:

```python
from alphasign.text_format import color, font, speed, date_code, CTRL_TIME
from alphasign.protocol import Color, Font

message = (
    color(Color.RED)
    + font(Font.SEVEN_HIGH_STD)
    + b"Temp: "
    + color(Color.YELLOW)
    + b"22.5\xb0C  "
    + color(Color.GREEN)
    + CTRL_TIME  # insert live clock
)

pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(message, mode=DisplayMode.ROTATE))
sign.send(pkt)
```

See [Text Formatting](api/text-formatting.md) for the full reference.

---

## Displaying Images

```python
from alphasign import Image
from alphasign.commands import WriteSmallDots, WriteSpecialFunction
from alphasign.protocol import FileType, DotsColorDepth

# Convert image to sign palette
img = Image("logo.png")

# Configure memory for the picture file
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.configure_memory([
    {
        "label": "P",
        "type": FileType.DOTS,
        "size": (img.height, img.width),
        "color_depth": DotsColorDepth.EIGHT_COLOR,
    }
]))
sign.send(pkt)

# Send the picture
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSmallDots(img.to_bytes(), label="P",
                       width=img.width, height=img.height))
sign.send(pkt)
```

---

## ACK/NAK Error Checking

Enable two-way error checking (Alpha 2.0+ signs):

```python
# Tell the sign to send ACK/NAK
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.enable_ack_nak(True))
sign.send(pkt)

# Enable client-side checking
sign.enable_ack_nak()

# Now send() will raise NAKError if the sign returns NAK
from alphasign.exceptions import NAKError
try:
    sign.send(pkt)
except NAKError as e:
    print(f"Sign rejected packet: {e}")
```

---

## Context Manager

```python
with Sign(sign_type=SignType.ALL) as sign:
    sign.open("/dev/ttyUSB0")
    sign.send(Packet().add(WriteText(b"Hello!")))
# sign.close() is called automatically
```

---

## Nesting Commands

Multiple commands can be placed in one packet (sent as nested commands):

```python
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.set_time(14, 30))
pkt.add(WriteSpecialFunction.set_day_of_week(DayOfWeek.MONDAY))
sign.send(pkt)
```

Each command gets its own STX/ETX/checksum frame inside a single transmission.
