"""Exceptions for the alphasign library."""

from __future__ import annotations


class AlphaSignError(Exception):
    """Base exception for all alphasign errors."""


class ConnectionError(AlphaSignError):
    """Raised when the serial connection cannot be opened or is lost."""


class PacketError(AlphaSignError):
    """Raised when a packet cannot be constructed."""


class ChecksumError(AlphaSignError):
    """Raised when a received packet fails checksum validation."""


class ProtocolError(AlphaSignError):
    """Raised when the protocol is violated (e.g. unexpected response)."""


class NAKError(AlphaSignError):
    """Raised when the sign responds with NAK (negative acknowledgement).

    Attributes:
        error_status: The Serial Error Status Register value returned by the sign.
    """

    def __init__(self, error_status: int) -> None:
        self.error_status = error_status
        bits = self._decode_status(error_status)
        super().__init__(f"Sign returned NAK (error status: 0x{error_status:02X} — {bits})")

    @staticmethod
    def _decode_status(status: int) -> str:
        flags: list[str] = []
        if status & 0x20:
            flags.append("illegal command/label")
        if status & 0x10:
            flags.append("checksum error")
        if status & 0x08:
            flags.append("buffer overflow")
        if status & 0x04:
            flags.append("serial timeout")
        if status & 0x02:
            flags.append("bit framing error")
        if status & 0x01:
            flags.append("parity error")
        return ", ".join(flags) if flags else "no specific error bits set"


class TimeoutError(AlphaSignError):
    """Raised when a read operation times out waiting for the sign."""


class InvalidParameterError(AlphaSignError):
    """Raised when an invalid parameter is passed to a command."""
