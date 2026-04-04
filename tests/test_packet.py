"""Tests for Packet construction and checksum calculation."""

from __future__ import annotations

from alphasign.commands.base import BaseCommand
from alphasign.packet import Packet
from alphasign.protocol import (
    BROADCAST_ADDRESS,
    DELAY,
    EOT,
    ETX,
    SOH,
    STX,
    SYNC,
)


class _SimpleCommand(BaseCommand):
    """Minimal command stub for packet tests."""

    def __init__(self, code: bytes, data: bytes) -> None:
        self.code = code
        self._data = data

    def to_bytes(self) -> bytes:
        return self._data


# ---------------------------------------------------------------------------
# Packet structure
# ---------------------------------------------------------------------------


def test_packet_starts_with_sync_and_header():
    pkt = Packet(type_code=b"Z", address="00")
    pkt.add(_SimpleCommand(b"A", b"hello"))
    raw = pkt.to_bytes()
    assert raw.startswith(SYNC + SOH + b"Z" + b"00")


def test_packet_ends_with_eot():
    pkt = Packet()
    pkt.add(_SimpleCommand(b"A", b"data"))
    raw = pkt.to_bytes()
    assert raw.endswith(EOT)


def test_packet_contains_stx_and_delay():
    pkt = Packet()
    pkt.add(_SimpleCommand(b"A", b"x"))
    raw = pkt.to_bytes()
    # STX appears once followed immediately by DELAY marker
    stx_idx = raw.index(STX)
    assert raw[stx_idx + 1 : stx_idx + 2] == DELAY


def test_packet_without_checksum_no_etx():
    """Without checksum and single command, ETX should be absent."""
    pkt = Packet()
    pkt.add(_SimpleCommand(b"A", b"hi"), checksum=False)
    raw = pkt.to_bytes()
    # ETX (0x03) should not appear (only one command, no checksum)
    assert ETX not in raw


def test_packet_with_checksum_has_etx():
    pkt = Packet()
    pkt.add(_SimpleCommand(b"A", b"hi"), checksum=True)
    raw = pkt.to_bytes()
    assert ETX in raw


def test_packet_nested_commands_all_have_etx():
    pkt = Packet()
    pkt.add(_SimpleCommand(b"A", b"first"), checksum=False)
    pkt.add(_SimpleCommand(b"E", b"second"), checksum=False)
    raw = pkt.to_bytes()
    assert raw.count(ETX) == 2


def test_packet_address_encoded_correctly():
    pkt = Packet(type_code=b"f", address="0A")
    pkt.add(_SimpleCommand(b"A", b"x"))
    raw = pkt.to_bytes()
    assert b"0A" in raw


# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------


def test_checksum_is_four_ascii_hex_chars():
    pkt = Packet()
    cmd = _SimpleCommand(b"A", b"test")
    cs = pkt._checksum(cmd.code, cmd.to_bytes())
    assert len(cs) == 4
    # All characters should be valid hex digits
    assert all(c in b"0123456789ABCDEF" for c in cs)


def test_checksum_correct_value():
    # checksum = sum(STX + code + data + ETX) % 65536
    code = b"A"
    data = b"test"
    expected_sum = sum(b"\x02" + code + data + b"\x03") % 65536
    expected = f"{expected_sum:04X}".encode()
    pkt = Packet()
    assert pkt._checksum(code, data) == expected


def test_checksum_excludes_delay_markers():
    """DELAY bytes embedded in data must be excluded from the checksum."""
    pkt = Packet()
    code = b"I"
    # Pixel data with a DELAY marker embedded
    data_with_delay = b"AAAA" + DELAY + b"BBBB"
    data_clean = b"AAAA" + b"BBBB"
    cs_with_delay = pkt._checksum(code, data_with_delay)
    cs_clean = pkt._checksum(code, data_clean)
    assert cs_with_delay == cs_clean


def test_checksum_wraps_at_16bit():
    """Checksum arithmetic should wrap at 65536 (mod 65536)."""
    pkt = Packet()
    # Build data that forces a large sum
    code = b"A"
    data = bytes([0xFF] * 260)  # very large sum
    cs = pkt._checksum(code, data)
    assert len(cs) == 4


def test_checksum_appears_after_etx_in_packet():
    pkt = Packet()
    cmd = _SimpleCommand(b"A", b"hello")
    pkt.add(cmd, checksum=True)
    raw = pkt.to_bytes()
    etx_idx = raw.index(ETX)
    # 4 checksum bytes follow ETX
    cs_bytes = raw[etx_idx + 1 : etx_idx + 5]
    expected = pkt._checksum(cmd.code, cmd.to_bytes())
    assert cs_bytes == expected


# ---------------------------------------------------------------------------
# Default arguments
# ---------------------------------------------------------------------------


def test_default_type_code_is_z():
    pkt = Packet()
    raw = pkt.to_bytes()
    assert b"Z" in raw[5:8]


def test_default_address_is_broadcast():
    pkt = Packet()
    raw = pkt.to_bytes()
    assert BROADCAST_ADDRESS.encode() in raw


def test_packet_chaining():
    """add() should return the Packet for chaining."""
    pkt = Packet()
    result = pkt.add(_SimpleCommand(b"A", b"x"))
    assert result is pkt
