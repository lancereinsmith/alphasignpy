"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from alphasign.sign import Sign
from alphasign.sign_types import SignType


@pytest.fixture(autouse=True)
def reset_sign_singleton():
    """Reset the Sign singleton before every test to avoid state leakage."""
    Sign._reset()
    yield
    Sign._reset()


@pytest.fixture
def sign():
    """Return a Sign instance with SignType.ALL (no port opened)."""
    return Sign(sign_type=SignType.ALL, address="00")


@pytest.fixture
def alpha_2x0c_sign():
    """Return a Sign instance configured for the Alpha 2X0C."""
    return Sign(sign_type=SignType.ALPHA_2X0C, address="01")
