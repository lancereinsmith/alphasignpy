---
icon: lucide/triangle-alert
---

# Exceptions

All exceptions inherit from `AlphaSignError` for easy catch-all handling.

```python
from alphasign.exceptions import (
    AlphaSignError,
    ConnectionError,
    PacketError,
    ChecksumError,
    ProtocolError,
    NAKError,
    TimeoutError,
    InvalidParameterError,
)
```

---

## Hierarchy

```
AlphaSignError
├── ConnectionError        — Serial port problems
├── PacketError            — Packet construction failures
├── ChecksumError          — Received checksum mismatch
├── ProtocolError          — Unexpected protocol response
├── NAKError               — Sign returned NAK
├── TimeoutError           — Read operation timed out
└── InvalidParameterError  — Bad argument to a command
```

---

## NAKError

Carries `error_status` — the Serial Error Status Register byte returned by the sign.

```python
from alphasign.exceptions import NAKError
from alphasign.protocol import SerialErrorStatus

try:
    sign.send(pkt)
except NAKError as e:
    print(f"Status register: 0x{e.error_status:02X}")
    if e.error_status & SerialErrorStatus.CHECKSUM_ERROR:
        print("Checksum error!")
```

### SerialErrorStatus bit masks

```python
from alphasign.protocol import SerialErrorStatus

SerialErrorStatus.ILLEGAL_COMMAND  # 0x20
SerialErrorStatus.CHECKSUM_ERROR   # 0x10
SerialErrorStatus.BUFFER_OVERFLOW  # 0x08
SerialErrorStatus.SERIAL_TIMEOUT   # 0x04
SerialErrorStatus.BIT_FRAMING      # 0x02
SerialErrorStatus.PARITY           # 0x01
SerialErrorStatus.DEFAULT          # 0x40  (bit 6 always 1)
```

---

## Example

```python
from alphasign.exceptions import AlphaSignError, NAKError, TimeoutError

try:
    sign.send(pkt)
except NAKError as e:
    print(f"Sign returned NAK: {e}")
except TimeoutError:
    print("Sign did not respond in time.")
except AlphaSignError as e:
    print(f"General sign error: {e}")
```
