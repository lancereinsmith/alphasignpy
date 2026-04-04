"""Sign type definitions.

Each ``SignDefinition`` captures the hardware characteristics of a specific
Alpha sign model.  The :class:`SignType` class exposes the pre-defined types
as class attributes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SignDefinition:
    """Hardware characteristics of a specific Alpha sign model.

    Attributes:
        name: Short identifier (e.g. ``"Alpha_2X0C"``).
        description: Human-readable model description.
        type_code: One-byte protocol type code (e.g. ``b"f"``).
        width: Display width in pixels.
        height: Display height in pixels.
        connection: Connection type (currently only ``"serial"``).
        default_baudrate: Default serial baud rate.
        features: Tuple of supported feature strings (e.g. ``("beep",)``).
    """

    name: str
    description: str
    type_code: bytes
    width: int
    height: int
    connection: str
    default_baudrate: int
    features: tuple[str, ...] = field(default_factory=tuple)

    def has_feature(self, feature: str) -> bool:
        """Return ``True`` if *feature* is supported by this sign."""
        return feature in self.features


class SignType:
    """Pre-defined sign type descriptors.

    Use one of these as the *sign_type* argument when constructing a
    :class:`~alphasign.sign.Sign`::

        sign = Sign(sign_type=SignType.ALPHA_2X0C)
    """

    ALL = SignDefinition(
        name="All",
        description="Generic / all signs (broadcast)",
        type_code=b"Z",
        width=255,
        height=255,
        connection="serial",
        default_baudrate=9600,
        features=(),
    )

    ALPHA_2X0C = SignDefinition(
        name="Alpha_2X0C",
        description="Alpha 210C / 220C",
        type_code=b"f",
        width=60,
        height=7,
        connection="serial",
        default_baudrate=9600,
        features=("beep",),
    )

    ALPHA_4200C = SignDefinition(
        name="Alpha_4200C",
        description="Alpha 4200C / 4240C",
        type_code=b"c",
        width=200,
        height=16,
        connection="serial",
        default_baudrate=9600,
        features=("beep",),
    )

    ALPHA_3600 = SignDefinition(
        name="Alpha_3600",
        description="AlphaEclipse 3600 (Alpha 3.0 protocol / RGB)",
        type_code=b"i",
        width=200,
        height=16,
        connection="serial",
        default_baudrate=9600,
        features=("beep", "rgb", "explode", "clock"),
    )

    @classmethod
    def from_type_code(cls, code: bytes) -> SignDefinition | None:
        """Return the :class:`SignDefinition` whose *type_code* matches *code*,
        or ``None`` if no match is found."""
        for attr in vars(cls).values():
            if isinstance(attr, SignDefinition) and attr.type_code == code:
                return attr
        return None

    @classmethod
    def exists(cls, name: str) -> bool:
        """Return ``True`` if a sign type with the given *name* exists."""
        for attr in vars(cls).values():
            if isinstance(attr, SignDefinition) and attr.name == name:
                return True
        return False
