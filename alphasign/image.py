"""Image conversion for Alpha Sign DOTS pictures.

:class:`Image` converts a standard RGB image (PNG, JPEG, etc.) to the
9-colour palette used by Alpha sign DOTS picture files.

The palette maps each pixel to its closest colour using Euclidean distance
in RGB space.

Example::

    from alphasign.image import Image
    from alphasign.commands.dots import WriteSmallDots

    img = Image("logo.png")
    cmd = WriteSmallDots(img.to_bytes(), label="A",
                         width=img.width, height=img.height)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from PIL.Image import Image as PilImageType


def _pil() -> Any:
    """Return the ``PIL.Image`` module, raising :exc:`ImportError` if Pillow is absent."""
    try:
        from PIL import Image

        return Image
    except ImportError as exc:
        raise ImportError(
            "Pillow is required for image conversion. Install it with: pip install Pillow"
        ) from exc


# 9-colour palette: (R, G, B) → pixel character
_PALETTE: dict[tuple[int, int, int], bytes] = {
    (0, 0, 0): b"0",  # Off / Black
    (255, 0, 0): b"1",  # Red
    (0, 255, 0): b"2",  # Green
    (255, 191, 0): b"3",  # Amber
    (187, 3, 0): b"4",  # Dim Red
    (0, 120, 0): b"5",  # Dim Green
    (83, 34, 35): b"6",  # Brown
    (255, 120, 0): b"7",  # Orange
    (255, 255, 0): b"8",  # Yellow
}


def _nearest_color(r: int, g: int, b: int) -> bytes:
    """Return the palette character for the nearest colour to *(r, g, b)*."""
    best_char = b"0"
    best_dist = float("inf")
    for (pr, pg, pb), char in _PALETTE.items():
        dist = math.sqrt((r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2)
        if dist < best_dist:
            best_dist = dist
            best_char = char
    return best_char


class Image:
    """Convert an image file to Alpha Sign DOTS pixel data.

    Args:
        source: Path to an image file, or a PIL ``Image`` object.

    Attributes:
        width: Image width in pixels.
        height: Image height in pixels.
        orig: The original PIL ``Image`` (RGB mode).

    Raises:
        ImportError: If Pillow is not installed.
        FileNotFoundError: If *source* is a path that does not exist.
    """

    def __init__(self, source: str | Any) -> None:
        pil_mod = _pil()
        if isinstance(source, str):
            self.orig: PilImageType = pil_mod.open(source).convert("RGB")
        else:
            self.orig = source.convert("RGB")  # type: ignore[union-attr]

        self.width: int = self.orig.width
        self.height: int = self.orig.height
        self._converted: bytes | None = None

    def convert(self) -> bytes:
        """Convert the image to Alpha Sign pixel data (cached after first call).

        Returns:
            Raw pixel data bytes: *height* rows of *width* colour characters,
            each row terminated with ``b"\\r"`` (CR, ``0x0D``).
        """
        if self._converted is not None:
            return self._converted

        rows: list[bytes] = []
        for y in range(self.height):
            row = b""
            for x in range(self.width):
                pixel = cast(tuple[int, int, int], self.orig.getpixel((x, y)))
                r, g, b = pixel
                row += _nearest_color(r, g, b)
            rows.append(row + b"\r")
        self._converted = b"".join(rows)
        return self._converted

    def to_bytes(self) -> bytes:
        """Return the converted pixel data (alias for :meth:`convert`)."""
        return self.convert()

    @classmethod
    def from_rgb_array(
        cls,
        pixels: list[list[tuple[int, int, int]]],
    ) -> Image:
        """Construct an :class:`Image` from a 2D list of RGB tuples.

        Args:
            pixels: ``pixels[y][x]`` = ``(R, G, B)`` tuple.

        Returns:
            A new :class:`Image` with the pixel data pre-converted.
        """
        pil_mod = _pil()
        h = len(pixels)
        w = len(pixels[0]) if h else 0
        pil_img = pil_mod.new("RGB", (w, h))
        for y, row in enumerate(pixels):
            for x, (r, g, b) in enumerate(row):
                pil_img.putpixel((x, y), (r, g, b))
        instance = cls.__new__(cls)
        instance.orig = pil_img.convert("RGB")
        instance.width = w
        instance.height = h
        instance._converted = None
        return instance
