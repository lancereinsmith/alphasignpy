---
icon: lucide/book-open
---

# Protocol Reference

The **Alpha Sign Communications Protocol** (also called M-Protocol) defines the
serial communication format for Alpha, BetaBrite, and compatible LED signs.

This page summarises the key protocol details implemented by alphasignpy.

---

## Packet Structure

```
[5× NUL]  [SOH]  [TypeCode]  [SignAddress]
  ( [STX] [CmdCode] [CmdData] [ETX] [Checksum] ) …
[EOT]
```

| Field | Byte(s) | Description |
|---|---|---|
| Sync | `0x00 × 5` | Baud-rate establishment via autobauding |
| SOH | `0x01` | Start of Header |
| TypeCode | 1 ASCII char | Sign type (e.g. `Z` = all, `f` = Alpha 210C) |
| SignAddress | 2 ASCII hex | Destination (`00` = broadcast) |
| STX | `0x02` | Start of Text — precedes every command |
| CmdCode | 1 ASCII char | Command code (A, E, G, I, …) |
| CmdData | variable | Command-specific data |
| ETX | `0x03` | End of Text — only present when checksum follows |
| Checksum | 4 ASCII hex | 16-bit sum of STX through ETX |
| EOT | `0x04` | End of Transmission |

For **nested** (multi-command) packets, multiple STX…ETX[Checksum] blocks appear
between the header and EOT.

---

## Checksum

```python
checksum = sum(STX + cmd_code + cmd_data + ETX) % 65536
formatted = f"{checksum:04X}"  # e.g. "1A2F"
```

The checksum is **optional** but strongly recommended.  Signs without
ACK/NAK enabled will silently reject packets with bad checksums.

alphasignpy automatically excludes `DELAY` (0xFF) timing markers from the
sum, since they are never transmitted to the sign.

---

## Serial Parameters

| Parameter | Default |
|---|---|
| Baud rate | 9600 |
| Data bits | 7 |
| Parity | Even |
| Stop bits | 1 |
| Character format | 7E1 |

All parameters are configurable via `sign.open()`.

---

## Timing

- **100 ms delay** required after STX when nesting commands (multi-command packets).
- **100 ms delay** required after the width bytes in DOTS picture commands.

alphasignpy handles timing automatically via `DELAY` (0xFF) markers embedded
in the byte stream.  `sign.send()` splits on these markers and sleeps 100 ms.

---

## Addressing

| Address | Meaning |
|---|---|
| `"00"` | Broadcast — all signs receive the packet |
| `"01"`–`"FF"` | Individual sign address |
| `"??"` | Wildcard (`?` = any hex nibble) |

Signs can be assigned a new address using
`WriteSpecialFunction.set_serial_address("0A")`.

---

## File Labels

Valid file labels: printable ASCII `0x20`–`0x7F`, **excluding**:

- `"?"` — reserved as wildcard
- `"1"`–`"5"` — reserved for counter target files (on counter-equipped signs)
- `"0"` — reserved for the **Priority TEXT file**

---

## Priority Text File

- Label `"0"` always exists (fixed 125-byte memory).
- No memory configuration required.
- Immediately overrides all other files when written.
- Clear by writing an empty message to label `"0"`.

---

## Memory Configuration

Before writing TEXT, STRING, or DOTS files (other than priority `"0"`), you
must allocate memory with `WriteSpecialFunction.configure_memory()`.

Memory configuration format per file: `F T P SIZE QQQQ`

| Field | Length | Description |
|---|---|---|
| `F` | 1 char | File label |
| `T` | 1 char | Type: `A`=TEXT, `B`=STRING, `D`=DOTS |
| `P` | 1 char | Protection: `U`=Unlocked, `L`=Locked |
| `SIZE` | 4 hex | Size in bytes (or H×W for DOTS) |
| `QQQQ` | 4 hex | TEXT: start/stop time; STRING: `0000`; DOTS: colour depth |

---

## ACK/NAK

Alpha 2.0+ signs support ACK/NAK handshaking.  When enabled:

1. Send `WriteSpecialFunction.enable_ack_nak(True)` to the sign.
2. Call `sign.enable_ack_nak()` to activate client-side checking.
3. After each `sign.send()`, the sign replies with:
   - `ACK` (`0x06`) + status byte — success
   - `NAK` (`0x15`) + status byte — failure

The status byte is the **Serial Error Status Register**:

| Bit | Mask | Meaning |
|---|---|---|
| 6 | `0x40` | Always 1 (default = `0x40`) |
| 5 | `0x20` | Illegal command code or file label |
| 4 | `0x10` | Checksum error |
| 3 | `0x08` | Serial buffer overflow |
| 2 | `0x04` | Serial timeout |
| 1 | `0x02` | Bit framing error |
| 0 | `0x01` | Parity error |

---

## Sign Type Codes

| Code | Sign |
|---|---|
| `Z` (0x5A) | All signs (wildcard / broadcast) |
| `!` (0x21) | Serial clock |
| `#` (0x23) | AlphaVision |
| `$` (0x24) | Full matrix AlphaVision |
| `f` (0x66) | Alpha 215C |
| `c` (0x63) | Alpha 4200C / 4240C |
| `i` (0x69) | Alpha 4200R / AlphaEclipse 3600 |
| `1` (0x31) | One-line signs |
| `2` (0x32) | Two-line signs |
| `0` (0x30) | Response code (sign → host) |

---

## Time Codes

Start and stop time codes are single hex bytes representing 10-minute
intervals across a 24-hour day:

| Code | Time |
|---|---|
| `0x00` | 12:00 am |
| `0x30` | 8:00 am |
| `0x60` | 4:00 pm |
| `0xFF` | Always (ignore stop time) |

---

## ASCII Printable Format

Not implemented — alphasignpy uses raw binary framing which is simpler
and more efficient.  The ASCII Printable format was designed for POCSAG
pagers that could not transmit bytes below `0x20`.
