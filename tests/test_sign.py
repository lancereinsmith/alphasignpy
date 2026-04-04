"""Tests for the Sign class (mocking serial I/O)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from alphasign.exceptions import ConnectionError, NAKError, ProtocolError, TimeoutError
from alphasign.packet import Packet
from alphasign.protocol import ACK, DELAY, NAK
from alphasign.sign import Sign
from alphasign.sign_types import SignType

# ---------------------------------------------------------------------------
# Sign construction and properties
# ---------------------------------------------------------------------------


def test_sign_type_properties(sign):
    assert sign.type_code == b"Z"
    assert sign.width == 255
    assert sign.height == 255
    assert sign.connection == "serial"
    assert sign.default_baudrate == 9600


def test_sign_alpha_2x0c_properties(alpha_2x0c_sign):
    assert alpha_2x0c_sign.type_code == b"f"
    assert alpha_2x0c_sign.width == 60
    assert alpha_2x0c_sign.height == 7
    assert alpha_2x0c_sign.has_feature("beep")
    assert not alpha_2x0c_sign.has_feature("rgb")


def test_sign_address(sign):
    assert sign.address == "00"


def test_sign_is_not_open_initially(sign):
    assert not sign.is_open


# ---------------------------------------------------------------------------
# open()
# ---------------------------------------------------------------------------


def test_open_serial_port():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial) as mock_cls:
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")

        mock_cls.assert_called_once_with(
            port="/dev/ttyUSB0",
            baudrate=9600,
            bytesize=7,
            parity="E",
            stopbits=1,
            timeout=1.0,
        )


def test_open_sets_dtr_false_by_default():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")

    assert mock_serial.dtr is False


def test_open_sets_dtr_true_when_requested():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0", dtr=True)

    assert mock_serial.dtr is True


def test_open_raises_on_serial_exception():
    import serial

    with patch("alphasign.sign.serial.Serial", side_effect=serial.SerialException("no port")):
        sign = Sign(sign_type=SignType.ALL)
        with pytest.raises(ConnectionError, match="Failed to open serial port"):
            sign.open("/dev/ttyUSB0")


def test_open_raises_when_port_not_open():
    mock_serial = MagicMock()
    mock_serial.is_open = False

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        with pytest.raises(ConnectionError, match="did not open"):
            sign.open("/dev/ttyUSB0")


def test_open_custom_baudrate():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial) as mock_cls:
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0", baudrate=19200)

        mock_cls.assert_called_once()
        _, kwargs = mock_cls.call_args
        assert kwargs["baudrate"] == 19200


# ---------------------------------------------------------------------------
# write() and send()
# ---------------------------------------------------------------------------


def test_write_raises_when_closed(sign):
    with pytest.raises(ConnectionError, match="not open"):
        sign.write(b"hello")


def test_write_sends_bytes():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.write(b"test")

    mock_serial.write.assert_called_once_with(b"test")


def test_send_splits_on_delay_markers():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        with patch("alphasign.sign.time.sleep") as mock_sleep:
            sign = Sign(sign_type=SignType.ALL)
            sign.open("/dev/ttyUSB0")
            sign.send(b"aaa" + DELAY + b"bbb")

    assert mock_sleep.call_count == 1
    # Both chunks written (no DELAY byte in either)
    calls = mock_serial.write.call_args_list
    written = b"".join(c.args[0] for c in calls)
    assert b"aaa" in written
    assert b"bbb" in written
    assert DELAY not in written


def test_send_packet_object():
    """send() should call to_bytes() on a Packet object."""
    pkt = Packet()

    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.send(pkt)

    mock_serial.write.assert_called()


# ---------------------------------------------------------------------------
# ACK/NAK
# ---------------------------------------------------------------------------


def test_ack_nak_not_enabled_by_default(sign):
    assert not sign._ack_nak_enabled


def test_enable_disable_ack_nak(sign):
    sign.enable_ack_nak()
    assert sign._ack_nak_enabled
    sign.disable_ack_nak()
    assert not sign._ack_nak_enabled


def test_enable_ack_nak_strict_default(sign):
    sign.enable_ack_nak()
    assert sign._ack_nak_strict is True


def test_enable_ack_nak_non_strict(sign):
    sign.enable_ack_nak(strict=False)
    assert sign._ack_nak_strict is False


def test_send_checks_ack_when_enabled():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.side_effect = [bytes([ACK]), b"\x40"]  # ACK + status

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak()
        sign.send(b"data")  # should not raise


def test_send_raises_nak_error():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.side_effect = [bytes([NAK]), bytes([0x10])]  # NAK + checksum error

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak()
        with pytest.raises(NAKError) as exc_info:
            sign.send(b"data")

    assert exc_info.value.error_status == 0x10


def test_send_raises_protocol_error_on_unknown_response_strict():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.return_value = bytes([0x55])  # unexpected

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak(strict=True)
        with pytest.raises(ProtocolError):
            sign.send(b"data")


def test_send_raises_timeout_when_no_ack_strict():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.return_value = b""  # timeout

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak(strict=True)
        with pytest.raises(TimeoutError):
            sign.send(b"data")


def test_send_no_raise_on_timeout_non_strict():
    """Non-strict mode: timeout is silently ignored — send() succeeds."""
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.return_value = b""  # sign does not respond

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak(strict=False)
        sign.send(b"data")  # must not raise


def test_send_non_strict_still_raises_nak():
    """NAK is always re-raised — even in non-strict mode."""
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.side_effect = [bytes([NAK]), bytes([0x10])]

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak(strict=False)
        with pytest.raises(NAKError):
            sign.send(b"data")


def test_send_non_strict_ignores_unexpected_byte():
    """Non-strict mode: unknown response byte is logged and ignored."""
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.return_value = bytes([0x55])  # unexpected byte

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.enable_ack_nak(strict=False)
        sign.send(b"data")  # must not raise


# ---------------------------------------------------------------------------
# read_response()
# ---------------------------------------------------------------------------


def test_read_response_returns_empty_on_timeout_by_default():
    """Default: no data → return b"" without raising."""
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.return_value = b""  # timeout

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        result = sign.read_response()

    assert result == b""


def test_read_response_raises_on_timeout_when_requested():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.read.return_value = b""

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        with pytest.raises(TimeoutError):
            sign.read_response(raise_on_timeout=True)


def test_read_response_reads_until_eot():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    # Sequence: 3 data bytes then EOT
    mock_serial.read.side_effect = [b"A", b"B", b"C", b"\x04"]

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        result = sign.read_response()

    assert result == b"ABC\x04"


def test_bytes_waiting_returns_zero_when_closed(sign):
    assert sign.bytes_waiting == 0


def test_bytes_waiting_returns_in_waiting():
    mock_serial = MagicMock()
    mock_serial.is_open = True
    mock_serial.in_waiting = 5

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        assert sign.bytes_waiting == 5


# ---------------------------------------------------------------------------
# close() / context manager
# ---------------------------------------------------------------------------


def test_close_closes_serial():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        sign.close()

    mock_serial.close.assert_called_once()


def test_context_manager_closes_on_exit():
    mock_serial = MagicMock()
    mock_serial.is_open = True

    with patch("alphasign.sign.serial.Serial", return_value=mock_serial):
        sign = Sign(sign_type=SignType.ALL)
        sign.open("/dev/ttyUSB0")
        with sign:
            pass

    mock_serial.close.assert_called()


# ---------------------------------------------------------------------------
# Singleton behaviour
# ---------------------------------------------------------------------------


def test_singleton_returns_same_instance():
    s1 = Sign(sign_type=SignType.ALL)
    s2 = Sign(sign_type=SignType.ALL)
    assert s1 is s2


def test_reset_allows_new_instance():
    s1 = Sign(sign_type=SignType.ALL)
    Sign._reset()
    s2 = Sign(sign_type=SignType.ALPHA_2X0C)
    assert s1 is not s2
    assert s2.type_code == b"f"
