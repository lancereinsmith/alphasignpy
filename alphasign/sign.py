"""Core Sign class — manages the serial connection and packet I/O.

Typical usage::

    from alphasign import Sign, SignType, Packet
    from alphasign.commands.text import WriteText

    sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
    sign.open("/dev/ttyUSB0", dtr=False)

    pkt = Packet(type_code=sign.type_code, address=sign.address)
    pkt.add(WriteText("Hello!"))
    sign.send(pkt)

    sign.close()
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import serial

from .exceptions import (
    ConnectionError,
    NAKError,
    ProtocolError,
    TimeoutError,
)
from .packet import Packet
from .protocol import ACK, BROADCAST_ADDRESS, DELAY, NAK
from .sign_types import SignDefinition, SignType
from .singleton import Singleton

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .packet import Packet


# Default serial parameters per the protocol spec
_DEFAULT_BAUDRATE = 9600
_DEFAULT_BYTESIZE = serial.SEVENBITS
_DEFAULT_PARITY = serial.PARITY_EVEN
_DEFAULT_STOPBITS = serial.STOPBITS_ONE
_DEFAULT_TIMEOUT = 1.0

# Delay between chunks when a DELAY marker is encountered (seconds)
_CHUNK_DELAY = 0.1

# Timeout when waiting for ACK/NAK (seconds)
_ACK_TIMEOUT = 2.0


class Sign(metaclass=Singleton):
    """Manages the serial connection to an Alpha sign.

    This class is a **singleton** — calling ``Sign(...)`` always returns the
    same instance.  To reset it (e.g. in tests) call ``Sign._reset()``.

    Args:
        sign_type: A :class:`~alphasign.sign_types.SignDefinition` describing
            the sign hardware.  Defaults to :attr:`~alphasign.sign_types.SignType.ALL`.
        address: Two-character hex address string (``"00"`` = broadcast).

    Attributes:
        ACK: Protocol ACK byte value (``0x06``).
        NAK: Protocol NAK byte value (``0x15``).
    """

    ACK = ACK
    NAK = NAK

    def __init__(
        self,
        sign_type: SignDefinition = SignType.ALL,
        address: str = BROADCAST_ADDRESS,
    ) -> None:
        self._sign_type = sign_type
        self.address = address
        self._ser: serial.Serial | None = None
        self._ack_nak_enabled: bool = False
        self._ack_nak_strict: bool = True

    # ------------------------------------------------------------------
    # Properties forwarded from SignDefinition
    # ------------------------------------------------------------------

    @property
    def type_code(self) -> bytes:
        """Protocol type code byte for this sign (e.g. ``b"Z"``)."""
        return self._sign_type.type_code

    @property
    def width(self) -> int:
        """Display width in pixels."""
        return self._sign_type.width

    @property
    def height(self) -> int:
        """Display height in pixels."""
        return self._sign_type.height

    @property
    def default_baudrate(self) -> int:
        """Default baud rate for this sign model."""
        return self._sign_type.default_baudrate

    @property
    def connection(self) -> str:
        """Connection type string (currently always ``"serial"``)."""
        return self._sign_type.connection

    def has_feature(self, feature: str) -> bool:
        """Return ``True`` if *feature* is supported by this sign model."""
        return self._sign_type.has_feature(feature)

    @property
    def is_open(self) -> bool:
        """``True`` if the serial port is currently open."""
        return self._ser is not None and self._ser.is_open

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def open(
        self,
        port: str,
        *,
        baudrate: int | None = None,
        bytesize: int = _DEFAULT_BYTESIZE,
        parity: str = _DEFAULT_PARITY,
        stopbits: float = _DEFAULT_STOPBITS,
        timeout: float = _DEFAULT_TIMEOUT,
        dtr: bool = False,
    ) -> None:
        """Open the serial port.

        The protocol specifies 7E1 framing (7 data bits, even parity, 1 stop
        bit) at 9600 baud by default.  All parameters can be overridden.

        Args:
            port: Serial port path (e.g. ``"/dev/ttyUSB0"`` or ``"COM3"``).
            baudrate: Baud rate.  Defaults to the sign type's
                ``default_baudrate`` (usually 9600).
            bytesize: Number of data bits.  Defaults to 7 (``SEVENBITS``).
            parity: Parity mode.  Defaults to even (``PARITY_EVEN``).
            stopbits: Number of stop bits.  Defaults to 1 (``STOPBITS_ONE``).
            timeout: Read timeout in seconds.  Defaults to 1.0.
            dtr: Set DTR line state after opening.  Defaults to ``False``
                (DTR low/disabled), which prevents accidental sign resets on
                some hardware configurations.

        Raises:
            ConnectionError: If the port cannot be opened.
        """
        # Close any existing connection first
        if self._ser and self._ser.is_open:
            self._ser.close()

        if self.connection != "serial":
            raise ConnectionError(f"Unsupported connection type: {self.connection!r}")

        baud = baudrate if baudrate is not None else self.default_baudrate

        try:
            self._ser = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
            )
        except serial.SerialException as exc:
            raise ConnectionError(f"Failed to open serial port {port!r}: {exc}") from exc

        if not self._ser.is_open:
            raise ConnectionError(f"Serial port {port!r} did not open successfully.")

        self._ser.dtr = dtr

    def close(self) -> None:
        """Close the serial port if it is open."""
        if self._ser and self._ser.is_open:
            self._ser.close()

    def __enter__(self) -> Sign:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    def write(self, data: bytes) -> None:
        """Write raw *data* bytes to the serial port.

        Args:
            data: Raw bytes to transmit.

        Raises:
            ConnectionError: If the port is not open.
        """
        if not self.is_open or self._ser is None:
            raise ConnectionError("Serial port is not open. Call open() first.")
        self._ser.write(data)

    def send(self, data: Packet | bytes) -> None:
        """Send a :class:`~alphasign.packet.Packet` or raw bytes to the sign.

        DELAY markers (``0xFF``) embedded in the byte stream are stripped and
        replaced with a 100 ms sleep, fulfilling the timing requirements of
        the protocol.

        After transmission, if ACK/NAK is enabled (via
        :meth:`enable_ack_nak`), the response is read and validated.

        Signs that do not support ACK/NAK will simply not send a response.
        Use ``enable_ack_nak(strict=False)`` to log a warning rather than
        raising in that case.

        Args:
            data: A :class:`~alphasign.packet.Packet` instance or raw bytes.

        Raises:
            ConnectionError: If the port is not open.
            NAKError: If ACK/NAK is enabled and the sign returns NAK.
            ProtocolError: If ACK/NAK is enabled (strict) and the response
                is an unexpected byte.
            TimeoutError: If ACK/NAK is enabled (strict) and no response
                arrives within the serial timeout.
        """
        payload = data.to_bytes() if isinstance(data, Packet) else data

        # Split on DELAY markers (0xFF) — send each chunk with 100 ms gaps
        chunks = payload.split(DELAY)
        for i, chunk in enumerate(chunks):
            if chunk:
                self.write(chunk)
            if i < len(chunks) - 1:
                time.sleep(_CHUNK_DELAY)

        if self._ack_nak_enabled:
            self._check_ack()

    def read(self, size: int = 1) -> bytes:
        """Read *size* bytes from the serial port.

        Args:
            size: Number of bytes to read.

        Returns:
            The bytes read (may be shorter than *size* on timeout).

        Raises:
            ConnectionError: If the port is not open.
        """
        if not self.is_open or self._ser is None:
            raise ConnectionError("Serial port is not open. Call open() first.")
        return self._ser.read(size)

    def read_response(self, *, raise_on_timeout: bool = False) -> bytes:
        """Read a complete response packet from the sign (until EOT).

        Many signs do not send a response to write commands at all.  By
        default this method returns ``b""`` when nothing arrives within the
        configured timeout so that calling code does not need to handle an
        exception for the normal case.  Set ``raise_on_timeout=True`` when
        you *require* a response (e.g. after a read command).

        Args:
            raise_on_timeout: If ``True``, raise :exc:`TimeoutError` when no
                data is received.  Defaults to ``False``.

        Returns:
            Bytes received up to and including EOT (``0x04``), or ``b""``
            if the sign did not respond and ``raise_on_timeout`` is ``False``.

        Raises:
            ConnectionError: If the port is not open.
            TimeoutError: If ``raise_on_timeout=True`` and no response arrives.
        """
        if not self.is_open or self._ser is None:
            raise ConnectionError("Serial port is not open. Call open() first.")

        buf = b""
        while True:
            byte = self._ser.read(1)
            if not byte:
                # Serial timeout — sign sent nothing (or we reached end of data)
                if not buf:
                    if raise_on_timeout:
                        raise TimeoutError("Timed out waiting for response from sign.")
                    _log.debug("read_response: no data received within timeout.")
                break
            buf += byte
            if byte == b"\x04":  # EOT
                break
        return buf

    # ------------------------------------------------------------------
    # ACK/NAK helpers
    # ------------------------------------------------------------------

    def enable_ack_nak(self, *, strict: bool = True) -> None:
        """Enable ACK/NAK checking for subsequent :meth:`send` calls.

        You must first send a ``WriteSpecialFunction.enable_ack_nak(True)``
        packet to configure the sign itself.  This method only enables the
        *client-side* validation.

        Args:
            strict: Controls behaviour when the sign does not respond:

                * ``True`` (default) — raise :exc:`TimeoutError`.  Use this
                  when you have confirmed the sign supports ACK/NAK.
                * ``False`` — log a warning and continue.  Use this when
                  working with mixed hardware or signs that may not respond.

        Example::

            # Tell the sign to start sending ACK/NAK
            sign.send(Packet().add(WriteSpecialFunction.enable_ack_nak(True)))
            # Enable client-side checking (lenient mode)
            sign.enable_ack_nak(strict=False)
        """
        self._ack_nak_enabled = True
        self._ack_nak_strict = strict

    def disable_ack_nak(self) -> None:
        """Disable ACK/NAK checking."""
        self._ack_nak_enabled = False

    @property
    def bytes_waiting(self) -> int:
        """Number of bytes currently in the serial receive buffer.

        Returns ``0`` when the port is not open.
        """
        if not self.is_open or self._ser is None:
            return 0
        return self._ser.in_waiting

    def _check_ack(self) -> None:
        """Read one byte and handle the ACK/NAK response.

        Behaviour on timeout (no response) is controlled by
        ``self._ack_nak_strict``:

        * ``True``  — raise :exc:`TimeoutError`.
        * ``False`` — log a debug warning and return silently.

        Raises:
            NAKError: Always — regardless of strict mode — when the sign
                returns NAK.  A NAK means the sign *received* the packet but
                *rejected* it; this is always actionable.
            ProtocolError: In strict mode, when the response byte is neither
                ACK nor NAK.
            TimeoutError: In strict mode, when no byte is received.
        """
        if self._ser is None:
            return

        byte = self._ser.read(1)

        if not byte:
            # Sign did not respond within the serial timeout
            if self._ack_nak_strict:
                raise TimeoutError("Timed out waiting for ACK/NAK from sign.")
            _log.debug(
                "ACK/NAK: no response received (sign may not support ACK/NAK "
                "or it was not enabled on the sign)."
            )
            return

        val = byte[0]

        if val == ACK:
            self._ser.read(1)  # consume the status register byte
            return

        if val == NAK:
            status_byte = self._ser.read(1)
            status = status_byte[0] if status_byte else 0
            raise NAKError(status)

        # Unexpected byte
        if self._ack_nak_strict:
            raise ProtocolError(
                f"Unexpected response byte 0x{val:02X} "
                f"(expected ACK 0x{ACK:02X} or NAK 0x{NAK:02X})."
            )
        _log.debug("ACK/NAK: unexpected byte 0x%02X — ignored (non-strict mode).", val)
