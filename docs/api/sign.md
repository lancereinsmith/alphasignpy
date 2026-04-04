---
icon: lucide/wifi
---

# Sign & Packet

## Sign

```python
from alphasign import Sign, SignType

sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
sign.open("/dev/ttyUSB0", dtr=False)
```

`Sign` is a **singleton metaclass** — only one instance exists per process.
Use `Sign._reset()` to discard the instance (useful in tests).

### Constructor

```python
Sign(sign_type=SignType.ALL, address="00")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sign_type` | `SignDefinition` | `SignType.ALL` | Hardware descriptor from `SignType`. |
| `address` | `str` | `"00"` | 2-char hex address. `"00"` = broadcast. |

### `open(port, *, baudrate, bytesize, parity, stopbits, timeout, dtr)`

Open the serial connection.

```python
sign.open(
    "/dev/ttyUSB0",
    baudrate=9600,      # default: sign type's default_baudrate
    bytesize=7,         # default: SEVENBITS (7E1 per protocol spec)
    parity="E",         # default: PARITY_EVEN
    stopbits=1,         # default: STOPBITS_ONE
    timeout=1.0,        # default: 1.0 s
    dtr=False,          # default: False (suppress DTR)
)
```

Raises `ConnectionError` if the port cannot be opened.

### `send(data)`

Send a `Packet` or raw bytes to the sign.

- Splits on `DELAY` markers (`0xFF`) and sleeps 100 ms between chunks.
- If `enable_ack_nak()` was called, reads back the sign's ACK/NAK response.

Raises:

- `ConnectionError` — port not open.
- `NAKError` — sign returned NAK.
- `ProtocolError` — unexpected response byte.
- `TimeoutError` — no ACK/NAK received within timeout.

### `read(size)`

Read *size* raw bytes from the port.

### `read_response()`

Read a full response packet (until `EOT`) from the sign.

### `close()`

Close the serial port. Also called automatically by the context manager.

### `enable_ack_nak()` / `disable_ack_nak()`

Toggle client-side ACK/NAK checking.  You must also send
`WriteSpecialFunction.enable_ack_nak(True)` to configure the sign itself.

### Properties

| Property | Type | Description |
|---|---|---|
| `type_code` | `bytes` | Protocol type byte (e.g. `b"f"`). |
| `width` | `int` | Display width in pixels. |
| `height` | `int` | Display height in pixels. |
| `default_baudrate` | `int` | Default baud rate for this sign. |
| `connection` | `str` | Connection type (`"serial"`). |
| `is_open` | `bool` | `True` if the port is open. |

---

## SignType

Pre-defined sign descriptors:

```python
from alphasign import SignType

SignType.ALL          # Generic / broadcast
SignType.ALPHA_2X0C   # Alpha 210C / 220C
SignType.ALPHA_4200C  # Alpha 4200C / 4240C
SignType.ALPHA_3600   # AlphaEclipse 3600 (Alpha 3.0 / RGB)
```

### `SignType.from_type_code(code)` → `SignDefinition | None`

Look up a `SignDefinition` by its protocol type code byte.

### `SignType.exists(name)` → `bool`

Check if a named sign type is defined.

---

## Packet

```python
from alphasign import Packet
from alphasign.commands import WriteText

pkt = Packet(type_code=b"Z", address="00")
pkt.add(WriteText(b"Hello!"))
sign.send(pkt)
```

### Constructor

```python
Packet(type_code=b"Z", address="00")
```

### `add(command, *, checksum=True)` → `Packet`

Append a command to the packet. Returns `self` for chaining.

All commands in a packet with `checksum=True` get individual
STX/ETX/checksum framing.

### `to_bytes()` → `bytes`

Serialise to protocol bytes.

**Wire format:**

```
[5× NUL] [SOH] [TypeCode] [SignAddr]
  [STX] [0xFF] [CmdCode] [CmdData] [ETX] [Checksum]
  ...
[EOT]
```

The `0xFF` byte is a **timing marker** — `sign.send()` strips it and sleeps
100 ms. It is never actually transmitted to the sign.

### Checksum

Computed as:

```python
sum(STX + cmd_code + cmd_data + ETX) % 65536
```

Formatted as 4 uppercase ASCII hex digits. DELAY (`0xFF`) markers are
excluded before summing, so the checksum matches what the sign actually
receives.
