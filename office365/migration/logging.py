"""Structured events and throttled progress for a migration run.

A migration is a long, headless job: a session over a dozen lists runs for an hour
while printing nothing between "Migrating…" and the final summary, unless the
caller wires the ``progress`` hook every job already accepts. This module supplies
the two pieces an operator needs and nothing else:

- one **JSON object per event** on the standard :mod:`logging` hierarchy, with a
  stable event vocabulary and a stable field set (so a dashboard can parse it), and
- :class:`ProgressReporter`, a throttled :data:`~office365.runtime.operations.
  ProgressCallback` that reduces per-item snapshots into a heartbeat with a rate
  and an ETA.

Nothing here knows about a log backend. Emit JSON lines and let the operator's own
pipeline ship them — an OpenTelemetry Collector's ``filelog``/``stdout`` receiver
into Loki or Azure Monitor, Promtail, a sidecar, ``kubectl logs -f``. Bringing the
vendor SDK in would make this library depend on a monitoring product, and a
library must not pick one for its caller.

Event vocabulary (payload fields in parentheses):

``run.started`` (``tasks``), ``run.completed`` (``duration_ms``, ``success``,
``skipped``, ``errors``)
    One migration session.
``plan.started`` / ``plan.completed`` (``source``, ``target``, ``items``,
``duration_ms``)
    A job's planning pass — which passes are actually jobs; a list pair is one job.
``job.started`` (``source``, ``target``, ``items``) and ``job.completed``
(``source``, ``target``, ``phase``, ``duration_ms``, ``success``, ``skipped``,
``errors``, ``bytes_transferred``) / ``job.failed`` (…, ``error``)
    One container (a list, a library, a site's root) for one job.
``progress`` (``done``, ``total``, ``percent``, ``rate``, ``eta_seconds``,
``elapsed_seconds``, ``stage``, ``subject``)
    A throttled heartbeat from :class:`ProgressReporter`; ``subject`` names the item
    it is about (a list title, a file) when the caller reported one.
``run.warning`` (``count``)
    A note a resolution step collected, emitted by a caller that ships logs
    (``session.warnings()`` is the same text). Notes are collected, not logged at
    ``warning``: a library that both logs a note and hands it to the caller prints
    every one of them twice.

Every record also carries ``ts`` (UTC ISO-8601 with milliseconds), ``level`` and
``logger``. Per-item events are deliberately absent: a five-hundred-thousand item
library must not produce five hundred thousand log lines, so items are counted and
only failures are worth a line of their own.

The checkpoint and the report files stay the **authoritative** record of a run —
logs are best-effort and must never be needed to resume one.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from office365.runtime.operations import Progress

__all__ = [
    "LOGGER_NAME",
    "JsonLogFormatter",
    "TextLogFormatter",
    "ProgressReporter",
    "configure_json_logging",
    "configure_text_logging",
    "log_event",
]

#: Every event this module emits goes through this logger, so a caller can route
#: migration events without touching the rest of the library's logging.
LOGGER_NAME = "office365.migration"

_RESERVED = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", None, None)).keys() | {"message", "asctime", "taskName", "event"}
)

logger = logging.getLogger(LOGGER_NAME)

_MINUTE = 60  # seconds and minutes per hour — one constant, two uses
#: Below this window a rate is noise, not a measurement, so it is reported as unknown.
_MIN_RATE_SECONDS = 0.5


def _utc_now() -> str:
    """A stable, sortable UTC timestamp (millisecond precision, ``Z`` suffix)."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class TextLogFormatter(logging.Formatter):
    """Render a log record as one readable line, with its event name when it has one.

    ``"warning  job.failed  library:/sites/t: denied"`` — the event name is what a
    filter or a grep needs, and a record from elsewhere in the library (no ``event``
    field) simply renders without it.
    """

    def __init__(self) -> None:
        super().__init__("%(levelname)-7s %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        line = super().format(record)
        event = getattr(record, "event", None)
        return f"{line}  [{event}]" if event else line


class JsonLogFormatter(logging.Formatter):
    """Render a log record as one JSON object per line.

    The record's message becomes ``message``; the ``event`` name and any extra
    fields passed to :func:`log_event` become top-level keys, so a filter or a query
    can select ``event = "job.failed"`` without parsing the message.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": _utc_now(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": getattr(record, "event", None) or "log",
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)


def configure_json_logging(stream: Any = None, level: int = logging.INFO) -> logging.Handler:
    """Route migration events to ``stream`` (default ``stderr``) as JSON lines.

    Replaces a handler this function installed earlier, so calling it twice does not
    duplicate every line. The rest of the library's logging is left alone: only
    :data:`LOGGER_NAME` is touched.

    Args:
        stream: A writable text stream; defaults to ``sys.stderr``.
        level: Minimum level for migration events (``logging.INFO`` by default).

    Returns:
        The installed handler, in case the caller wants to remove or re-route it.
    """
    for handler in list(logger.handlers):
        if getattr(handler, "_office365_json", False):
            logger.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonLogFormatter())
    handler._office365_json = True  # type: ignore[attr-defined]
    logger.addHandler(handler)
    if logger.level == logging.NOTSET or logger.level > level:
        logger.setLevel(level)
    return handler


def configure_text_logging(stream: Any = None, level: int = logging.INFO) -> logging.Handler:
    """Route migration events to ``stream`` (default ``stderr``) as plain lines.

    The human-readable counterpart of :func:`configure_json_logging` — same events,
    same level filtering, one line each (``warning  job.failed  library:/sites/t:
    denied``), for a run whose progress is being watched rather than collected. Also
    replaces a handler installed by an earlier call, and touches only
    :data:`LOGGER_NAME`.

    Args:
        stream: A writable text stream; defaults to ``sys.stderr``.
        level: Minimum level for migration events (``logging.INFO`` by default).

    Returns:
        The installed handler, in case the caller wants to remove or re-route it.
    """
    for handler in list(logger.handlers):
        if getattr(handler, "_office365_text", False):
            logger.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(TextLogFormatter())
    handler.setLevel(level)
    handler._office365_text = True  # type: ignore[attr-defined]
    logger.addHandler(handler)
    if logger.level == logging.NOTSET or logger.level > level:
        logger.setLevel(level)
    return handler


def log_event(event: str, message: Optional[str] = None, *, level: int = logging.INFO, **fields: Any) -> None:
    """Emit one structured migration event.

    Args:
        event: A name from the vocabulary in this module's docstring
            (``job.completed``, ``progress``, …).
        message: Human-readable text; defaults to the event name, because a reader
            of the raw stream rarely wants an empty message.
        level: Standard logging level.
        **fields: Structured payload — counters, labels, durations. Must not shadow
            a :class:`logging.LogRecord` attribute (``msg``, ``args``, …).
    """
    logger.log(level, message or event, extra={"event": event, **fields})


class ProgressReporter:
    """Reduce per-item progress snapshots to a throttled heartbeat.

    The runner calls a progress hook once per item; writing a line per item is how
    a migration log becomes unreadable (and how a log pipeline becomes expensive).
    This reporter keeps the counters, computes a rate and an ETA, and emits at most
    one ``progress`` event per ``interval`` seconds — or one per container, whichever
    comes first, because a container that finishes before the interval is worth a
    final line.

    It is a plain :data:`ProgressCallback`, so it drops into ``session.start(...)``,
    ``job.run(...)`` and every long-running runtime operation unchanged.

    Args:
        interval: Minimum seconds between heartbeats (``0`` emits on every snapshot
            and is meant for debugging).
        emit: Callable receiving the heartbeat payload; by default it is logged as a
            ``progress`` event. Pass a printer to keep the human console output.
        clock: Monotonic clock, injectable for tests.
        label: Optional container label included in every heartbeat.

    Example:
        >>> reporter = ProgressReporter(interval=30, label="Documents")
        >>> session.start(progress=reporter)  # heartbeats while it runs
        >>> print(reporter.summary())  # "… 1,234/5,000 (24.7%) 41.2/s ETA 1m31s"
    """

    def __init__(
        self,
        interval: float = 15.0,
        *,
        emit: Optional[Callable[[dict], None]] = None,
        clock: Callable[[], float] = time.monotonic,
        label: str = "",
    ) -> None:
        self.interval = max(0.0, float(interval))
        self.label = label
        self._emit = emit or (lambda payload: log_event("progress", **payload))
        self._clock = clock
        self._started = clock()
        self._last_emit = self._started
        self._done = 0
        self._total: Optional[int] = None
        self._stage = ""
        #: The item the current snapshot is about (a list title, a file name), when
        #: the caller names one; it is what a heartbeat line leads with.
        self._subject: Optional[str] = None
        self._beat = 0
        self._emitted_done = -1
        # A shared reporter is handed to every concurrently-running job, so the
        # counters and the emit call are taken under one lock (re-entrant: an emit
        # hook may report back into the same reporter).
        self._lock = threading.RLock()

    # ── ProgressCallback ─────────────────────────────────────────

    def __call__(self, progress: Progress) -> None:
        with self._lock:
            self._observe(progress)

    def _observe(self, progress: Progress) -> None:
        total = progress.total
        stage = progress.stage or self._stage
        # Two things restart the measurement window: a different container (its
        # total) and a different stage (planning -> copying). A rate carried over
        # from one into the other is not about the work being reported, and it
        # produced the classic "planning, ETA 81h" line. The *first* total does not
        # restart anything, so a single-container run is measured from its start.
        new_total = total is not None and self._total is not None and total != self._total
        new_stage = bool(self._stage) and stage != self._stage
        if new_total or new_stage:
            self._done = 0
            self._started = self._clock()
            self._last_emit = self._started
        if total is not None:
            self._total = total
        elif new_stage:
            # A stage that reports no total ("pages", "navigation") is
            # indeterminate: keeping the previous stage's total would print a
            # percentage that is no longer about anything.
            self._total = None
        items = getattr(progress, "items", None)
        if items:
            self._subject = str(items[0])
        self._done = progress.done
        self._stage = stage
        now = self._clock()
        if self.interval == 0 or now - self._last_emit >= self.interval:
            self.flush(now=now)

    def derive(self, label: str = "") -> "ProgressReporter":
        """A sibling reporter with its own counters, sharing this one's settings.

        Concurrency gives every job its own container window (and label) while the
        interval, clock and ``emit`` sink stay the session's — so the heartbeats of
        two lists running at once do not fight over one set of counters.
        """
        return ProgressReporter(self.interval, emit=self._emit, clock=self._clock, label=label or self.label)

    # ── Reporting ────────────────────────────────────────────────

    def flush(self, *, now: Optional[float] = None) -> dict:
        """Emit a heartbeat now (if there is anything to report) and return it."""
        with self._lock:
            return self._flush(now=now)

    def _flush(self, *, now: Optional[float] = None) -> dict:
        now = self._clock() if now is None else now
        payload = self.snapshot(now=now)
        self._last_emit = now
        self._emitted_done = self._done
        self._beat += 1
        payload["beat"] = self._beat
        self._emit(payload)
        return payload

    def snapshot(self, *, now: Optional[float] = None) -> dict:
        """The heartbeat payload without emitting it (rate and ETA included)."""
        now = self._clock() if now is None else now
        elapsed = max(0.0, now - self._started)
        rate = self._done / elapsed if elapsed >= _MIN_RATE_SECONDS and self._done else None
        eta = None
        if rate and self._total is not None and self._total > self._done:
            eta = (self._total - self._done) / rate
        percent = None
        if self._total:
            percent = round(min(100.0, self._done / self._total * 100), 1)
        return {
            "label": self.label,
            "subject": self._subject,
            "stage": self._stage,
            "done": self._done,
            "total": self._total,
            "percent": percent,
            "rate": round(rate, 2) if rate is not None else None,
            "eta_seconds": round(eta, 1) if eta is not None else None,
            "elapsed_seconds": round(elapsed, 1),
        }

    def close(self) -> str:
        """Emit a last heartbeat (so the final count is not lost) and summarise."""
        if self._done != self._emitted_done:
            self.flush()
        return self.summary()

    def summary(self) -> str:
        """One human-readable line for the current counters."""
        snap = self.snapshot()
        parts = [f"{snap['done']:,}"]
        if snap["total"]:
            parts[0] += f"/{snap['total']:,} ({snap['percent']}%)"
        if snap["rate"]:
            parts.append(f"{snap['rate']:g}/s")
        if snap["eta_seconds"] is not None:
            parts.append(f"ETA {_duration(snap['eta_seconds'])}")
        elif snap["total"] and snap["done"] >= snap["total"]:
            parts.append("done")
        head = f"{self.label}: " if self.label else ""
        return head + " ".join(parts)


def _duration(seconds: float) -> str:
    """``91`` -> ``"1m31s"`` — an ETA readable at a glance."""
    seconds = int(round(seconds))
    if seconds < _MINUTE:
        return f"{seconds}s"
    minutes, rest = divmod(seconds, _MINUTE)
    if minutes < _MINUTE:
        return f"{minutes}m{rest:02d}s"
    hours, minutes = divmod(minutes, _MINUTE)
    return f"{hours}h{minutes:02d}m"
