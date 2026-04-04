"""Singleton metaclass."""

from __future__ import annotations

from typing import Any, ClassVar


class Singleton(type):
    """Metaclass that restricts a class to a single instance.

    Typical use::

        class MyClass(metaclass=Singleton):
            ...

    Call ``MyClass._reset()`` in tests to discard the cached instance.
    """

    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def _reset(cls) -> None:
        """Discard the cached instance (useful for testing)."""
        cls._instances.pop(cls, None)
