"""Write SPECIAL FUNCTION (command E) and Read SPECIAL FUNCTION (command F).

Special functions control sign hardware settings, memory, timing, display
sequences, audio, and the ACK/NAK protocol.  Each function is exposed as a
separate factory class method on :class:`WriteSpecialFunction`.

Protocol reference: sections 3.5 (Write) and 3.6 (Read), plus all sub-sections.
"""

from __future__ import annotations

from ..exceptions import InvalidParameterError
from ..protocol import (
    CommandCode,
    DayOfWeek,
    DotsColorDepth,
    FileProtection,
    FileType,
    SpecialFunction,
    TimeFormat,
)
from .base import BaseCommand

# ---------------------------------------------------------------------------
# Write SPECIAL FUNCTION — command E
# ---------------------------------------------------------------------------


class WriteSpecialFunction(BaseCommand):
    """Build a Write SPECIAL FUNCTION packet (command ``E``).

    Do not instantiate directly — use the factory class methods instead::

        cmd = WriteSpecialFunction.set_time(14, 30)
        cmd = WriteSpecialFunction.clear_memory()
        cmd = WriteSpecialFunction.enable_ack_nak(True)

    Each factory method returns a ready-to-use :class:`WriteSpecialFunction`.
    """

    code = CommandCode.WRITE_SPECIAL.value

    def __init__(self, function: SpecialFunction, payload: bytes) -> None:
        self._function = function
        self._payload = payload

    def to_bytes(self) -> bytes:
        return self._function.value + self._payload

    # ------------------------------------------------------------------
    # Time / date
    # ------------------------------------------------------------------

    @classmethod
    def set_time(cls, hours: int, minutes: int) -> WriteSpecialFunction:
        """Set the sign's real-time clock.

        Args:
            hours: Hour in 24-hour format (0-23).
            minutes: Minute (0-59).

        Raises:
            InvalidParameterError: If values are out of range.
        """
        if not (0 <= hours <= 23):
            raise InvalidParameterError(f"hours must be 0-23, got {hours}.")
        if not (0 <= minutes <= 59):
            raise InvalidParameterError(f"minutes must be 0-59, got {minutes}.")
        payload = f"{hours:02d}{minutes:02d}".encode()
        return cls(SpecialFunction.SET_TIME, payload)

    @classmethod
    def set_date(cls, month: int, day: int, year: int) -> WriteSpecialFunction:
        """Set the sign's calendar date.

        Args:
            month: Month (1-12).
            day: Day (1-31).
            year: Two-digit year (0-99).
        """
        if not (1 <= month <= 12):
            raise InvalidParameterError(f"month must be 1-12, got {month}.")
        if not (1 <= day <= 31):
            raise InvalidParameterError(f"day must be 1-31, got {day}.")
        if not (0 <= year <= 99):
            raise InvalidParameterError(f"year must be 0-99, got {year}.")
        payload = f"{month:02d}{day:02d}{year:02d}".encode()
        return cls(SpecialFunction.SET_DATE, payload)

    @classmethod
    def set_day_of_week(cls, day: DayOfWeek) -> WriteSpecialFunction:
        """Set the day of the week on the sign's clock.

        Args:
            day: A :class:`~alphasign.protocol.DayOfWeek` value.
        """
        return cls(SpecialFunction.DAY_OF_WEEK, day.value)

    @classmethod
    def set_time_format(cls, fmt: TimeFormat) -> WriteSpecialFunction:
        """Set 12-hour (standard) or 24-hour (military) time display.

        Args:
            fmt: A :class:`~alphasign.protocol.TimeFormat` value.
        """
        return cls(SpecialFunction.TIME_FORMAT, fmt.value)

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------

    @classmethod
    def set_speaker(cls, enabled: bool) -> WriteSpecialFunction:
        """Enable or disable the sign's built-in speaker.

        Args:
            enabled: ``True`` to enable, ``False`` to disable.
        """
        payload = b"00" if enabled else b"FF"
        return cls(SpecialFunction.SPEAKER, payload)

    @classmethod
    def generate_tone(
        cls,
        tone_type: int,
        frequency: int = 0,
        duration: int = 5,
        repeat: int = 0,
    ) -> WriteSpecialFunction:
        """Generate an audible tone.

        Args:
            tone_type: ``1`` for preset tone, ``2`` for variable frequency tone.
            frequency: Frequency value (0-FF hex) — only for *tone_type* 2.
            duration: Duration (0-F hex, in tenths of a second).
            repeat: Repeat count (0-F hex).

        Raises:
            InvalidParameterError: If *tone_type* is invalid.
        """
        if tone_type not in (1, 2):
            raise InvalidParameterError(f"tone_type must be 1 or 2, got {tone_type}.")
        if tone_type == 1:
            payload = b"\x31"
        else:
            if not (0 <= frequency <= 0xFF):
                raise InvalidParameterError(f"frequency must be 0-255, got {frequency}.")
            payload = b"\x32" + f"{frequency:02X}{duration:01X}{repeat:01X}".encode()
        return cls(SpecialFunction.TONE, payload)

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    @classmethod
    def clear_memory(cls) -> WriteSpecialFunction:
        """Clear all configured memory on the sign.

        .. warning::
            This erases all text, string, and picture files.  The priority
            text file and the default file ``"A"`` survive.
        """
        return cls(SpecialFunction.MEMORY_CONFIG, b"$$$")

    @classmethod
    def configure_memory(
        cls,
        files: list[dict],
    ) -> WriteSpecialFunction:
        """Configure memory allocation for one or more files.

        Each entry in *files* is a dict with the following keys:

        * ``"label"`` (str) — one-character file label.
        * ``"type"`` (:class:`~alphasign.protocol.FileType`) — ``TEXT``,
          ``STRING``, or ``DOTS``.
        * ``"protection"`` (:class:`~alphasign.protocol.FileProtection`) —
          ``UNLOCKED`` or ``LOCKED``.  Defaults to ``UNLOCKED``.
        * ``"size"`` (int) — file size in bytes (for TEXT/STRING), **or**
          a ``(height, width)`` tuple (for DOTS).
        * ``"start_time"`` (int, TEXT only) — start time code (0x00-0xFF).
          Defaults to ``0xFF`` (always).
        * ``"stop_time"`` (int, TEXT only) — stop time code.
          Defaults to ``0xFF`` (always).
        * ``"color_depth"`` (:class:`~alphasign.protocol.DotsColorDepth`, DOTS
          only) — Defaults to ``EIGHT_COLOR``.

        Example::

            cmd = WriteSpecialFunction.configure_memory([
                {"label": "A", "type": FileType.TEXT, "size": 256},
                {"label": "B", "type": FileType.STRING, "size": 64},
                {"label": "P", "type": FileType.DOTS, "size": (16, 60),
                 "color_depth": DotsColorDepth.EIGHT_COLOR},
            ])
        """
        payload = b""
        for entry in files:
            label: str = entry["label"]
            ftype: FileType = entry["type"]
            protection: FileProtection = entry.get("protection", FileProtection.UNLOCKED)
            size = entry["size"]

            payload += label.encode()
            payload += ftype.value
            payload += protection.value

            if ftype is FileType.DOTS and isinstance(size, tuple):
                h, w = size
                # Protocol stores image size as height x width in hex
                payload += f"{h:02X}{w:02X}".encode()
            else:
                payload += f"{int(size):04X}".encode()

            if ftype is FileType.TEXT:
                start = entry.get("start_time", 0xFF)
                stop = entry.get("stop_time", 0xFF)
                payload += f"{start:02X}{stop:02X}".encode()
            elif ftype is FileType.STRING:
                payload += b"0000"
            elif ftype is FileType.DOTS:
                depth: DotsColorDepth = entry.get("color_depth", DotsColorDepth.EIGHT_COLOR)
                payload += depth.value

        return cls(SpecialFunction.MEMORY_CONFIG, payload)

    # ------------------------------------------------------------------
    # Display scheduling
    # ------------------------------------------------------------------

    @classmethod
    def set_run_time_table(
        cls, label: str, start_time: int, stop_time: int
    ) -> WriteSpecialFunction:
        """Set the start and stop display time for a TEXT file.

        Args:
            label: One-character TEXT file label.
            start_time: Start time code (0x00-0xFF; 0xFF = always).
            stop_time: Stop time code (0x00-0xFF; 0xFF = always).
        """
        if not (0x00 <= start_time <= 0xFF and 0x00 <= stop_time <= 0xFF):
            raise InvalidParameterError("Time codes must be in range 0x00-0xFF.")
        payload = label.encode() + f"{start_time:02X}".encode() + f"{stop_time:02X}".encode()
        return cls(SpecialFunction.RUN_TIME_TABLE, payload)

    @classmethod
    def set_run_sequence(cls, sequence: str | bytes) -> WriteSpecialFunction:
        """Set the display run sequence (order in which files are shown).

        Args:
            sequence: Sequence string, e.g. ``"KABAC"`` where ``K`` sets the
                sequence type and subsequent pairs are file labels.
        """
        payload = sequence.encode() if isinstance(sequence, str) else sequence
        return cls(SpecialFunction.RUN_SEQUENCE, payload)

    @classmethod
    def set_run_day_table(cls, label: str, start_day: int, stop_day: int) -> WriteSpecialFunction:
        """Set the days of the week on which a TEXT file runs.

        Args:
            label: One-character TEXT file label.
            start_day: Day code byte.
            stop_day: Day code byte.
        """
        payload = label.encode() + bytes([start_day]) + bytes([stop_day])
        return cls(SpecialFunction.RUN_DAY_TABLE, payload)

    # ------------------------------------------------------------------
    # Dimming
    # ------------------------------------------------------------------

    @classmethod
    def set_dimming_register(cls, dim_mode: int, brightness_percent: int) -> WriteSpecialFunction:
        """Set the sign's brightness level.

        Args:
            dim_mode: Dimming mode byte (0x00-0xFF).
            brightness_percent: Target brightness as a percentage.  Rounded to
                the nearest supported level: 100, 86, 72, 58, or 44.

        Raises:
            InvalidParameterError: If *brightness_percent* is out of range.
        """
        if not (0 <= brightness_percent <= 100):
            raise InvalidParameterError(
                f"brightness_percent must be 0-100, got {brightness_percent}."
            )
        levels = [100, 86, 72, 58, 44]
        index = min(range(len(levels)), key=lambda i: abs(levels[i] - brightness_percent))
        payload = f"{dim_mode:02X}{index:02d}".encode()
        return cls(SpecialFunction.DIMMING_REG, payload)

    @classmethod
    def set_dimming_times(cls, start_code: int, stop_code: int) -> WriteSpecialFunction:
        """Set the dimming schedule using time codes.

        Args:
            start_code: Start time code (0x00-0xFF).
            stop_code: Stop time code (0x00-0xFF).
        """
        payload = f"{start_code:02X}{stop_code:02X}".encode()
        return cls(SpecialFunction.DIMMING_TIMES, payload)

    # ------------------------------------------------------------------
    # XY display
    # ------------------------------------------------------------------

    @classmethod
    def display_at_xy(
        cls,
        x: int,
        y: int,
        text: str | bytes,
        enabled: bool = True,
    ) -> WriteSpecialFunction:
        """Display text at a specific pixel position.

        Args:
            x: Horizontal pixel position.
            y: Vertical pixel position.
            text: Text to display.
            enabled: ``True`` to enable, ``False`` to disable XY mode.
        """
        status = b"+" if enabled else b"-"
        text_bytes = text.encode() if isinstance(text, str) else text
        payload = status + b"+" + f"{x:02d}{y:02d}".encode() + text_bytes
        return cls(SpecialFunction.XY_POSITION, payload)

    # ------------------------------------------------------------------
    # Hardware control
    # ------------------------------------------------------------------

    @classmethod
    def soft_reset(cls) -> WriteSpecialFunction:
        """Perform a software reset of the sign."""
        return cls(SpecialFunction.SOFT_RESET, b"")

    @classmethod
    def set_serial_address(cls, address: str) -> WriteSpecialFunction:
        """Assign a new serial address to the sign.

        Args:
            address: Two-character hex address (``"01"``-``"FF"``).
        """
        if len(address) != 2:
            raise InvalidParameterError(
                f"Serial address must be 2 hex characters, got {address!r}."
            )
        return cls(SpecialFunction.SERIAL_ADDRESS, address.encode())

    @classmethod
    def clear_error_status(cls) -> WriteSpecialFunction:
        """Clear the Serial Error Status Register."""
        return cls(SpecialFunction.CLEAR_ERROR, b"")

    # ------------------------------------------------------------------
    # ACK/NAK
    # ------------------------------------------------------------------

    @classmethod
    def enable_ack_nak(cls, enabled: bool = True) -> WriteSpecialFunction:
        """Enable or disable ACK/NAK responses from the sign.

        Args:
            enabled: ``True`` to enable (sign sends ACK/NAK after each packet),
                ``False`` to disable.
        """
        payload = b"1" if enabled else b"0"
        return cls(SpecialFunction.ACK_NAK, payload)

    # ------------------------------------------------------------------
    # Counter
    # ------------------------------------------------------------------

    @classmethod
    def set_counter(
        cls,
        counters: list[dict],
    ) -> WriteSpecialFunction:
        """Program up to 5 hardware counters.

        Each entry in *counters* is a dict with keys:

        * ``"control"`` (int) — control byte (see protocol spec section 3.5.E5).
        * ``"start_time"`` (int) — start time (2 hex chars).
        * ``"stop_time"`` (int) — stop time (2 hex chars).
        * ``"start_value"`` (int) — 8-digit BCD start value.
        * ``"change_value"`` (int) — 8-digit BCD change value.
        * ``"current_value"`` (int) — 8-digit BCD current value.
        * ``"target_value"`` (int) — 8-digit BCD target value.
        * ``"target_files"`` (int) — target file bitmask byte.
        * ``"change_minutes"`` (int) — minute sync (0-59).
        * ``"change_hours"`` (int) — hour sync (0-23).

        Missing fields default to 0.
        """
        if len(counters) > 5:
            raise InvalidParameterError("A maximum of 5 counters can be configured.")

        payload = b""
        for c in counters:
            ctrl = c.get("control", 0)
            t_start = c.get("start_time", 0)
            t_stop = c.get("stop_time", 0)
            v_start = c.get("start_value", 0)
            v_change = c.get("change_value", 0)
            v_current = c.get("current_value", 0)
            v_target = c.get("target_value", 0)
            t_files = c.get("target_files", 0)
            m_minutes = c.get("change_minutes", 0)
            m_hours = c.get("change_hours", 0)
            payload += (
                f"{ctrl:02X}{t_start:02X}{t_stop:02X}"
                f"{v_start:08d}{v_change:08d}{v_current:08d}{v_target:08d}"
                f"{t_files:02X}{m_minutes:02X}{m_hours:02X}"
            ).encode()

        return cls(SpecialFunction.SET_COUNTER, payload)

    # ------------------------------------------------------------------
    # Large Dots memory
    # ------------------------------------------------------------------

    @classmethod
    def configure_large_dots_memory(
        cls,
        files: list[dict],
        append: bool = False,
    ) -> WriteSpecialFunction:
        """Configure LARGE DOTS picture memory (functions ``8`` / ``9``).

        Args:
            files: List of dicts, each with:

                * ``"name"`` (str) — up to 9-character filename.
                * ``"protection"`` (:class:`~alphasign.protocol.FileProtection`).
                * ``"rows"`` (int) — number of pixel rows.
                * ``"cols"`` (int) — number of pixel columns.
                * ``"colors"`` (str) — ``"01"`` mono, ``"02"`` tricolor,
                  ``"08"`` RGB (Alpha 3.0+).

            append: If ``True``, use the Append function (``9``) instead of Set.
        """
        payload = b""
        for f in files:
            name = f.get("name", "").ljust(9)[:9]
            prot: FileProtection = f.get("protection", FileProtection.UNLOCKED)
            rows = f.get("rows", 0)
            cols = f.get("cols", 0)
            colors = f.get("colors", "01")
            payload += (
                name.encode()
                + prot.value
                + f"{rows:04X}{cols:04X}".encode()
                + colors.encode()
                + b"0000"
            )

        func = SpecialFunction.APPEND_LARGE_DOTS if append else SpecialFunction.LARGE_DOTS_CONFIG
        return cls(func, payload)


# ---------------------------------------------------------------------------
# Read SPECIAL FUNCTION — command F
# ---------------------------------------------------------------------------


class ReadSpecialFunction(BaseCommand):
    """Request a special function value from the sign (command ``F``).

    Args:
        function: The :class:`~alphasign.protocol.SpecialFunction` to read.

    Example::

        from alphasign.commands.special import ReadSpecialFunction
        from alphasign.protocol import SpecialFunction

        # Request current time
        cmd = ReadSpecialFunction(SpecialFunction.SET_TIME)
        pkt = Packet().add(cmd)
        sign.send(pkt)
        response = sign.read_response()
    """

    code = CommandCode.READ_SPECIAL.value

    def __init__(self, function: SpecialFunction) -> None:
        self._function = function

    def to_bytes(self) -> bytes:
        return self._function.value


def parse_general_info(response: bytes) -> dict:
    """Parse a ``F"`` (General Info) response into a dict.

    Returns a dict with keys: ``firmware``, ``date``, ``time``,
    ``time_format``, ``speaker``, ``memory_pool``, ``memory_free``.
    """
    try:
        stx_idx = response.index(b"\x02")
        # Skip STX + "F" + function byte
        payload = response[stx_idx + 3 :]
        # Strip leading NUL
        if payload and payload[0] == 0x00:
            payload = payload[1:]
        result: dict = {}
        result["firmware"] = payload[0:8].decode(errors="replace").strip()
        result["firmware_rev"] = chr(payload[8])
        result["date"] = payload[9:13].decode(errors="replace")
        result["time"] = payload[13:17].decode(errors="replace")
        result["time_format"] = chr(payload[17])
        result["speaker"] = payload[18:20].decode(errors="replace")
        mem = payload[20:].split(b",")
        result["memory_pool"] = int(mem[0], 16) if mem else 0
        result["memory_free"] = int(mem[1][:4], 16) if len(mem) > 1 else 0
        return result
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Could not parse General Info response: {exc}") from exc
