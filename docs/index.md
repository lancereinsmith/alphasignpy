---
icon: lucide/zap
---

# alphasignpy

A comprehensive, modern Python library for controlling **Alpha Sign** LED displays
over serial (RS-232 / USB-to-serial).

Implements the full **Alpha Sign Communications Protocol (M-Protocol)**,
including all command types, special functions, ACK/NAK error checking,
memory configuration, and image display.

---

## Features

- **Comprehensive protocol coverage** — Write/Read TEXT (A/B), STRING (G/H), SMALL
  DOTS (I/J), LARGE DOTS (M/N), RGB DOTS (K/L), SPECIAL FUNCTIONS (E/F), and
  ALPHAVISION BULLETIN (O/OT).
- **Error checking** — Optional ACK/NAK handshake; full exception hierarchy.
- **DTR control** — Set or suppress DTR on serial open to prevent accidental
  sign resets.
- **Image conversion** — Automatic conversion from any RGB image to the sign's
  9-colour palette using Euclidean nearest-neighbour colour matching.
- **Text formatting helpers** — Fluent API for colours, fonts, speed, date,
  time, animation, and counters.
- **Comprehensive test suite** — 210 tests, all passing, with serial I/O mocked
  for offline development.

---

## Quick Start

```python
from alphasign import Sign, Packet, SignType
from alphasign.commands import WriteText, WriteSpecialFunction
from alphasign.protocol import DisplayMode, Color, FileType

# Open a connection
sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
sign.open("/dev/ttyUSB0", dtr=False)

# Configure a TEXT file in memory (one-time setup)
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.configure_memory([
    {"label": "A", "type": FileType.TEXT, "size": 256},
]))
sign.send(pkt)

# Send a message
from alphasign.text_format import color, font
from alphasign.protocol import Color, Font

msg = color(Color.RED) + b"Hello " + color(Color.GREEN) + b"World!"
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(msg, label="A", mode=DisplayMode.ROTATE))
sign.send(pkt)

sign.close()
```

---

## Installation

```bash
pip install alphasignpy
```

Or from source:

```bash
git clone https://github.com/lancereinsmith/python-alphasign.git
cd python-alphasign
pip install -e ".[dev]"
```

---

## Credits

Original library by [prototux](mailto:jason@prototux.net).
Rewritten and extended by Lance Reinsmith.
