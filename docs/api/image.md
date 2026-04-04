---
icon: lucide/image
---

# Image

```python
from alphasign import Image
```

Converts any RGB image (PNG, JPEG, BMP, etc.) to the 9-colour palette used by
Alpha sign DOTS picture files, using Euclidean nearest-neighbour colour matching.

Requires **Pillow** (`pip install Pillow`).

---

## Image Class

### `Image(source)`

```python
img = Image("logo.png")           # from file path
img = Image(pil_image_object)     # from an existing PIL Image
```

### `image.to_bytes()` → `bytes`

Return the converted pixel data.

Format: *height* rows of *width* `PixelColor` characters, each row terminated
with `b"\r"` (CR, `0x0D`).

The first call converts the image; subsequent calls return the cached result.

### `image.width`, `image.height`

Dimensions of the original image in pixels.

### `Image.from_rgb_array(pixels)` → `Image`

Construct from a 2D list of `(R, G, B)` tuples:

```python
pixels = [
    [(255, 0, 0), (0, 255, 0)],  # row 0: red, green
    [(0, 0, 0),   (255, 255, 0)], # row 1: black, yellow
]
img = Image.from_rgb_array(pixels)
```

---

## Colour Palette

| Code | Character | Colour |
|---|---|---|
| `b"0"` | `0` | Off / Black |
| `b"1"` | `1` | Red |
| `b"2"` | `2` | Green |
| `b"3"` | `3` | Amber |
| `b"4"` | `4` | Dim Red |
| `b"5"` | `5` | Dim Green |
| `b"6"` | `6` | Brown |
| `b"7"` | `7` | Orange |
| `b"8"` | `8` | Yellow |

---

## Full Example

```python
from alphasign import Image, Packet, Sign, SignType
from alphasign.commands import WriteSmallDots, WriteSpecialFunction
from alphasign.protocol import DotsColorDepth, FileType

img = Image("logo.png")

sign = Sign(sign_type=SignType.ALPHA_2X0C, address="01")
sign.open("/dev/ttyUSB0", dtr=False)

# Configure memory
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSpecialFunction.configure_memory([
    {
        "label": "P",
        "type": FileType.DOTS,
        "size": (img.height, img.width),
        "color_depth": DotsColorDepth.EIGHT_COLOR,
    }
]))
sign.send(pkt)

# Send picture
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSmallDots(img.to_bytes(), label="P",
                       width=img.width, height=img.height))
sign.send(pkt)

sign.close()
```
