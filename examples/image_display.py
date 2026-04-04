"""Display an image on the sign using Small Dots.

Requires Pillow: pip install Pillow
"""

import time

from alphasign import Image, Packet, Sign, SignType
from alphasign.commands import WriteSmallDots, WriteSpecialFunction, WriteText
from alphasign.protocol import FileType
from alphasign.text_format import picture_ref

IMG_PATH = "test.png"  # any small RGB image

sign = Sign(sign_type=SignType.ALL, address="00")
sign.open("/dev/ttyUSB0", dtr=False)

# Convert image to the 9-colour sign palette.
img = Image(IMG_PATH)
print(f"Image: {img.width}x{img.height}")

# Allocate memory for the image (label "A") and a TEXT file (label "B")
# that references it.
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(
    WriteSpecialFunction.configure_memory(
        [
            {"label": "A", "type": FileType.DOTS, "size": (img.height, img.width)},
            {"label": "B", "type": FileType.TEXT, "size": 64},
        ]
    )
)
sign.send(pkt)
time.sleep(1)

# Upload the converted pixel data.
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteSmallDots(img.to_bytes(), label="A", width=img.width, height=img.height))
sign.send(pkt)
time.sleep(0.5)

# Write a TEXT file that displays the picture inline.
pkt = Packet(type_code=sign.type_code, address=sign.address)
pkt.add(WriteText(picture_ref("A"), label="B"))
sign.send(pkt)

sign.close()
