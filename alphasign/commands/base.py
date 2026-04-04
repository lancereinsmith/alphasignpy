"""Base class for all Alpha Sign command objects."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract base for all protocol command objects.

    Every concrete command must declare a ``code`` class attribute (the
    one-byte protocol command code) and implement :meth:`to_bytes`.
    """

    #: One-byte protocol command code (e.g. ``b"A"`` for Write TEXT).
    code: bytes

    @abstractmethod
    def to_bytes(self) -> bytes:
        """Return the command's data field as bytes (excluding the command code).

        The returned bytes will be framed by the :class:`~alphasign.packet.Packet`
        with STX, ETX, and optionally a checksum.
        """
