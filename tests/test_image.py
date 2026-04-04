"""Tests for Image conversion."""

from __future__ import annotations

import pytest

try:
    from PIL import Image as PilImage

    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

from alphasign.image import Image, _nearest_color

pytestmark = pytest.mark.skipif(
    not _PIL_AVAILABLE,
    reason="Pillow is not installed",
)


# ---------------------------------------------------------------------------
# _nearest_color helper
# ---------------------------------------------------------------------------


def test_nearest_color_pure_red():
    assert _nearest_color(255, 0, 0) == b"1"


def test_nearest_color_pure_green():
    assert _nearest_color(0, 255, 0) == b"2"


def test_nearest_color_black():
    assert _nearest_color(0, 0, 0) == b"0"


def test_nearest_color_yellow():
    assert _nearest_color(255, 255, 0) == b"8"


def test_nearest_color_orange():
    assert _nearest_color(255, 120, 0) == b"7"


# ---------------------------------------------------------------------------
# Image construction
# ---------------------------------------------------------------------------


def _make_pil_image(width: int, height: int, color_rgb: tuple) -> PilImage.Image:
    img = PilImage.new("RGB", (width, height), color_rgb)
    return img


def test_image_dimensions():
    pil_img = _make_pil_image(10, 5, (255, 0, 0))
    img = Image(pil_img)
    assert img.width == 10
    assert img.height == 5


def test_image_to_bytes_returns_bytes():
    pil_img = _make_pil_image(4, 2, (0, 0, 0))
    img = Image(pil_img)
    result = img.to_bytes()
    assert isinstance(result, bytes)


def test_image_to_bytes_row_count():
    """Output should have exactly `height` rows."""
    pil_img = _make_pil_image(3, 4, (255, 0, 0))
    img = Image(pil_img)
    rows = img.to_bytes().split(b"\r")
    # split gives one trailing empty element after last \r
    non_empty = [r for r in rows if r]
    assert len(non_empty) == 4


def test_image_to_bytes_row_width():
    """Each row should contain exactly `width` colour characters."""
    w, h = 5, 3
    pil_img = _make_pil_image(w, h, (0, 255, 0))  # all green → "2"
    img = Image(pil_img)
    rows = [r for r in img.to_bytes().split(b"\r") if r]
    for row in rows:
        assert len(row) == w


def test_image_all_red_pixels():
    """Solid red image → all pixel chars should be '1'."""
    pil_img = _make_pil_image(3, 3, (255, 0, 0))
    img = Image(pil_img)
    data = img.to_bytes().replace(b"\r", b"")
    assert all(b == ord("1") for b in data)


def test_image_all_black_pixels():
    pil_img = _make_pil_image(2, 2, (0, 0, 0))
    img = Image(pil_img)
    data = img.to_bytes().replace(b"\r", b"")
    assert all(b == ord("0") for b in data)


def test_image_conversion_is_cached():
    pil_img = _make_pil_image(4, 4, (255, 255, 0))
    img = Image(pil_img)
    r1 = img.to_bytes()
    r2 = img.to_bytes()
    assert r1 is r2  # same object (cached)


def test_image_from_rgb_array():
    pixels = [
        [(255, 0, 0), (0, 255, 0)],
        [(0, 0, 0), (255, 255, 0)],
    ]
    img = Image.from_rgb_array(pixels)
    assert img.width == 2
    assert img.height == 2
    data = img.to_bytes()
    rows = [r for r in data.split(b"\r") if r]
    assert rows[0] == b"12"  # red, green
    assert rows[1] == b"08"  # black, yellow


def test_image_rows_end_with_cr():
    pil_img = _make_pil_image(3, 2, (255, 0, 0))
    img = Image(pil_img)
    data = img.to_bytes()
    # Data should end with CR after each row
    assert data.count(b"\r") == 2
