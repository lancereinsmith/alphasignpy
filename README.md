# alphasignpy

A comprehensive, modern Python library for controlling **Alpha Sign** LED displays over serial.

Full implementation of the **Alpha Sign Communications Protocol (M-Protocol)**.

> Original [library](https://github.com/prototux/python-alphasign) by [prototux](mailto:jason@prototux.net). Rewritten and extended by Lance Reinsmith.

---

## Documentation

Full API documentation is available at [https://lancereinsmith.github.io/alphasignpy/](https://lancereinsmith.github.io/alphasignpy/)

---

## Features

- Comprehensive protocol coverage — Write/Read TEXT, STRING, SMALL/LARGE/RGB DOTS, SPECIAL FUNCTIONS, ALPHAVISION BULLETIN
- ACK/NAK error checking with full exception hierarchy
- DTR control to prevent accidental sign resets
- Image conversion from any RGB image to the 9-colour sign palette
- Text formatting helpers — colours, fonts, speed, date/time, animation, counters

## Installation

```bash
pip install alphasignpy
```

## Quick Start

```python
from alphasign import Sign, Packet, SignType
from alphasign.commands import WriteText, WriteSpecialFunction
from alphasign.protocol import DisplayMode, Color, FileType
from alphasign.text_format import color

# Open connection
sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
sign.open("/dev/ttyUSB0", dtr=False)

# Configure memory (one-time setup)
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.configure_memory([
    {"label": "A", "type": FileType.TEXT, "size": 256},
]))
sign.send(pkt)

# Send a coloured message
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(
    color(Color.RED) + b"Hello " + color(Color.GREEN) + b"World!",
    label="A",
    mode=DisplayMode.ROTATE,
))
sign.send(pkt)

sign.close()
```

## Protocol Notes

- Serial framing: 9600 baud, 7E1 (7 data bits, even parity, 1 stop bit)
- Uses binary framing (not ASCII Printable format)
- Timing markers (`0xFF`) are used to insert 100 ms delays; never transmitted
- Checksums are 16-bit hex sums from STX through ETX

## License

MIT License. See [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.
The original library by [prototux](mailto:jason@prototux.net) was released
under the Apache License 2.0.
