"""DOTS picture commands.

Three picture formats are supported:

* **Small Dots** (I/J) — up to 255x31 pixels, 9 colours.
* **Large Dots** (M/N) — up to 65535x65535 pixels, 9 colours, with optional
  run-length compression.
* **RGB Dots** (K/L) — 24-bit RGB per pixel (Alpha 3.0 / AlphaEclipse 3600 only).

Protocol reference: sections 3.9-3.14.
"""

from __future__ import annotations

from ..exceptions import InvalidParameterError
from ..protocol import DELAY, CommandCode, PixelColor
from .base import BaseCommand

# ---------------------------------------------------------------------------
# SMALL DOTS (I / J)
# ---------------------------------------------------------------------------


class WriteSmallDots(BaseCommand):
    """Write a SMALL DOTS picture file (command ``I``).

    Each pixel is a single ASCII character from :class:`~alphasign.protocol.PixelColor`.
    Rows are terminated with CR (``0x0D``).

    Args:
        pixel_data: Raw pixel data bytes — ``height`` rows of ``width``
            :class:`~alphasign.protocol.PixelColor` characters, each row
            terminated with ``b"\\r"`` (``0x0D``).
        label: One-character file label (must be pre-configured in memory).
        width: Image width in pixels (0-255).
        height: Image height in pixels (0-31).
        compress: If ``True``, apply run-length encoding before sending.

    The easiest way to build *pixel_data* is via
    :class:`~alphasign.image.Image`::

        from alphasign.image import Image
        from alphasign.commands.dots import WriteSmallDots

        img = Image("logo.png")
        cmd = WriteSmallDots(img.to_bytes(), label="A",
                             width=img.width, height=img.height)
    """

    code = CommandCode.WRITE_SMALL_DOTS.value

    def __init__(
        self,
        pixel_data: bytes,
        label: str = "A",
        width: int = 0,
        height: int = 0,
        compress: bool = False,
    ) -> None:
        if height > 31:
            raise InvalidParameterError(
                f"SMALL DOTS height {height} exceeds maximum of 31 pixels."
            )
        if width > 255:
            raise InvalidParameterError(f"SMALL DOTS width {width} exceeds maximum of 255 pixels.")
        self.pixel_data = pixel_data
        self.label = label
        self.width = width
        self.height = height
        self.compress = compress

    def to_bytes(self) -> bytes:
        data = self.label.encode()
        data += f"{self.height:02X}{self.width:02X}".encode()
        # DELAY marker — sign needs 100 ms after width bytes before row data
        data += DELAY
        data += self._compress() if self.compress else self.pixel_data
        return data

    def _compress(self) -> bytes:
        """Apply run-length encoding to the pixel data.

        Format: ``0x11 XX C`` where ``XX`` is the repeat count (hex, 1-based)
        and ``C`` is the colour character.  Runs shorter than 4 bytes are not
        compressed.
        """
        out = b""
        i = 0
        while i < len(self.pixel_data):
            byte = self.pixel_data[i : i + 1]
            if byte == b"\r":
                out += byte
                i += 1
                continue
            # Count run
            run = 1
            while (
                i + run < len(self.pixel_data)
                and self.pixel_data[i + run : i + run + 1] == byte
                and self.pixel_data[i + run : i + run + 1] != b"\r"
                and run < 0xFF
            ):
                run += 1
            if run >= 4:
                out += b"\x11" + f"{run - 1:02X}".encode() + byte
            else:
                out += byte * run
            i += run
        return out


class ReadSmallDots(BaseCommand):
    """Request a SMALL DOTS picture from the sign (command ``J``).

    Args:
        label: The label of the picture file to read.
    """

    code = CommandCode.READ_SMALL_DOTS.value

    def __init__(self, label: str = "A") -> None:
        self.label = label

    def to_bytes(self) -> bytes:
        return self.label.encode()


# ---------------------------------------------------------------------------
# LARGE DOTS (M / N)
# ---------------------------------------------------------------------------


class WriteLargeDots(BaseCommand):
    """Write a LARGE DOTS picture file (command ``M``).

    Identical to :class:`WriteSmallDots` but supports larger dimensions
    (width and height as 4-digit hex) and run-length compression.

    Args:
        pixel_data: Raw pixel data bytes (same format as SMALL DOTS).
        label: One-character file label.
        width: Image width in pixels (0-65535).
        height: Image height in pixels (0-65535).
        compress: If ``True``, apply run-length encoding.
    """

    code = CommandCode.WRITE_LARGE_DOTS.value

    def __init__(
        self,
        pixel_data: bytes,
        label: str = "A",
        width: int = 0,
        height: int = 0,
        compress: bool = False,
    ) -> None:
        if height > 0xFFFF or width > 0xFFFF:
            raise InvalidParameterError(
                f"LARGE DOTS dimensions ({width}x{height}) exceed maximum of 65535."
            )
        self.pixel_data = pixel_data
        self.label = label
        self.width = width
        self.height = height
        self.compress = compress

    def to_bytes(self) -> bytes:
        data = self.label.encode()
        data += f"{self.height:04X}{self.width:04X}".encode()
        data += DELAY
        data += self._compress() if self.compress else self.pixel_data
        return data

    def _compress(self) -> bytes:
        """Run-length encode using the LARGE DOTS CTR-Q format."""
        out = b""
        i = 0
        while i < len(self.pixel_data):
            byte = self.pixel_data[i : i + 1]
            if byte == b"\r":
                out += byte
                i += 1
                continue
            run = 1
            while (
                i + run < len(self.pixel_data)
                and self.pixel_data[i + run : i + run + 1] == byte
                and self.pixel_data[i + run : i + run + 1] != b"\r"
                and run < 0xFF
            ):
                run += 1
            if run >= 4:
                out += b"\x11" + f"{run - 1:02X}".encode() + byte
            else:
                out += byte * run
            i += run
        return out


class ReadLargeDots(BaseCommand):
    """Request a LARGE DOTS picture from the sign (command ``N``)."""

    code = CommandCode.READ_LARGE_DOTS.value

    def __init__(self, label: str = "A") -> None:
        self.label = label

    def to_bytes(self) -> bytes:
        return self.label.encode()


# ---------------------------------------------------------------------------
# RGB DOTS (K / L)  — Alpha 3.0 / AlphaEclipse 3600 only
# ---------------------------------------------------------------------------


class WriteRGBDots(BaseCommand):
    """Write an RGB DOTS picture file (command ``K``).

    Each pixel is represented as 6 ASCII hex digits: ``RRGGBB``.
    Rows are terminated with CR (``0x0D``).

    Alpha 3.0 protocol only (AlphaEclipse 3600 signs).

    Args:
        pixel_data: Raw RGB pixel data bytes.
        label: One-character file label.
        width: Image width in pixels.
        height: Image height in pixels.
        compress: If ``True``, apply run-length encoding (``0x11 XX RRGGBB``).
    """

    code = CommandCode.WRITE_RGB_DOTS.value

    def __init__(
        self,
        pixel_data: bytes,
        label: str = "A",
        width: int = 0,
        height: int = 0,
        compress: bool = False,
    ) -> None:
        self.pixel_data = pixel_data
        self.label = label
        self.width = width
        self.height = height
        self.compress = compress

    def to_bytes(self) -> bytes:
        data = self.label.encode()
        data += f"{self.height:04X}{self.width:04X}".encode()
        data += DELAY
        data += self._compress() if self.compress else self.pixel_data
        return data

    def _compress(self) -> bytes:
        """Run-length encode RGB pixels (6-char groups)."""
        out = b""
        i = 0
        while i < len(self.pixel_data):
            if self.pixel_data[i : i + 1] == b"\r":
                out += b"\r"
                i += 1
                continue
            pixel = self.pixel_data[i : i + 6]
            if len(pixel) < 6:
                out += pixel
                break
            run = 1
            while (
                i + run * 6 + 6 <= len(self.pixel_data)
                and self.pixel_data[i + run * 6 : i + run * 6 + 6] == pixel
                and run < 0xFF
            ):
                run += 1
            if run >= 2:
                out += b"\x11" + f"{run - 1:02X}".encode() + pixel
            else:
                out += pixel
            i += run * 6
        return out


class ReadRGBDots(BaseCommand):
    """Request an RGB DOTS picture from the sign (command ``L``)."""

    code = CommandCode.READ_RGB_DOTS.value

    def __init__(self, label: str = "A") -> None:
        self.label = label

    def to_bytes(self) -> bytes:
        return self.label.encode()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_pixel_row(pixels: list[PixelColor]) -> bytes:
    """Build a single row of pixel data from a list of :class:`~alphasign.protocol.PixelColor`.

    Each colour is encoded as its single-character ASCII code, and the row is
    terminated with CR (``0x0D``).

    Example::

        row = build_pixel_row([PixelColor.RED, PixelColor.OFF, PixelColor.GREEN])
        # b"102\\r"
    """
    return b"".join(p.value for p in pixels) + b"\r"


def build_rgb_row(pixels: list[tuple[int, int, int]]) -> bytes:
    """Build a single row of RGB pixel data.

    Args:
        pixels: A list of ``(R, G, B)`` tuples (0-255 per channel).

    Returns:
        Row bytes: each pixel as 6 ASCII hex chars, terminated with CR.
    """
    row = b"".join(f"{r:02X}{g:02X}{b:02X}".encode() for r, g, b in pixels)
    return row + b"\r"
