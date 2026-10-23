import json
import logging
import tempfile
import unittest
from pathlib import Path

from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.job import MigrationJob
from office365.migration.logging import (
    LOGGER_NAME,
    JsonLogFormatter,
    ProgressReporter,
    configure_json_logging,
    configure_text_logging,
    log_event,
)
from office365.runtime.operations import Progress


class _Capture(logging.Handler):
    """Collect records instead of rendering them (extras survive)."""

    def __init__(self):
        super().__init__()
        self.records: list = []

    def emit(self, record):
        self.records.append(record)


class _LogTestCase(unittest.TestCase):
    def capture(self) -> _Capture:
        handler = _Capture()
        logger = logging.getLogger(LOGGER_NAME)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.addCleanup(logger.removeHandler, handler)
        return handler

    @staticmethod
    def events(handler: _Capture, name: str) -> list:
        return [record for record in handler.records if getattr(record, "event", None) == name]


class TestJsonLogFormatter(unittest.TestCase):
    def test_a_record_becomes_one_json_object(self):
        record = logging.LogRecord(LOGGER_NAME, logging.WARNING, __file__, 1, "boom", None, None)
        record.event = "job.failed"
        record.error = "file is checked out"

        payload = json.loads(JsonLogFormatter().format(record))

        self.assertEqual(payload["level"], "warning")
        self.assertEqual(payload["logger"], LOGGER_NAME)
        self.assertEqual(payload["event"], "job.failed")
        self.assertEqual(payload["message"], "boom")
        self.assertEqual(payload["error"], "file is checked out")
        self.assertTrue(payload["ts"].endswith("Z"))


class TestConfigureJsonLogging(unittest.TestCase):
    def test_configuring_twice_does_not_duplicate_every_line(self):
        import io

        stream = io.StringIO()
        first = configure_json_logging(stream)
        second = configure_json_logging(stream)
        logger = logging.getLogger(LOGGER_NAME)
        self.addCleanup(logger.removeHandler, second)

        self.assertIsNot(first, second)
        self.assertNotIn(first, logger.handlers)
        self.assertEqual(sum(1 for h in logger.handlers if getattr(h, "_office365_json", False)), 1)
        log_event("run.started", tasks=0)
        self.assertEqual(len([line for line in stream.getvalue().splitlines() if line.strip()]), 1)


class TestProgressReporter(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.beats: list = []
        self.reporter = ProgressReporter(interval=10, emit=self.beats.append, clock=lambda: self.now, label="Documents")

    def test_a_snapshot_past_the_interval_is_reported(self):
        self.now = 10.0
        self.reporter(Progress(done=25, total=100, stage="migrating"))

        self.assertEqual(len(self.beats), 1)
        beat = self.beats[0]
        self.assertEqual(beat["done"], 25)
        self.assertEqual(beat["total"], 100)
        self.assertEqual(beat["percent"], 25.0)
        self.assertEqual(beat["stage"], "migrating")
        self.assertEqual(beat["label"], "Documents")
        self.assertEqual(beat["beat"], 1)

    def test_closing_reports_a_count_the_interval_swallowed(self):
        self.reporter(Progress(done=7, total=10))

        summary = self.reporter.close()

        self.assertEqual(len(self.beats), 1)
        self.assertEqual(self.beats[0]["done"], 7)
        self.assertEqual(summary, "Documents: 7/10 (70.0%)")

    def test_a_derived_reporter_shares_the_sink_and_keeps_its_own_counters(self):
        other = self.reporter.derive("Documents/Sub")
        self.now = 10.0

        self.reporter(Progress(done=5, total=10, stage="structure"))
        other(Progress(done=1, total=2, stage="structure"))

        self.assertEqual([beat["label"] for beat in self.beats], ["Documents", "Documents/Sub"])
        self.assertEqual([beat["done"] for beat in self.beats], [5, 1])
        self.assertEqual(self.reporter.summary(), "Documents: 5/10 (50.0%) 0.5/s ETA 10s")
        self.assertEqual(other.summary(), "Documents/Sub: 1/2 (50.0%) 0.1/s ETA 10s")


class TestMigrationEvents(_LogTestCase):
    def test_a_failing_job_reports_the_failure_and_still_raises(self):
        handler = self.capture()

        class _BrokenTarget:
            def label(self):
                return "broken"

            def configure(self, options):
                raise RuntimeError("cannot reach the target")

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            source.mkdir()
            (source / "a.txt").write_text("alpha")
            job = MigrationJob(FileSystemSource(source), _BrokenTarget())
            job.plan()
            with self.assertRaises(RuntimeError):
                job.run()

        failed = self.events(handler, "job.failed")[0]
        self.assertEqual(failed.error, "cannot reach the target")  # type: ignore[attr-defined]
        self.assertEqual(failed.levelname, "ERROR")


class TestConfigureTextLogging(unittest.TestCase):
    def test_configuring_twice_does_not_duplicate_every_line(self):
        import io

        stream = io.StringIO()
        first = configure_text_logging(stream)
        second = configure_text_logging(stream)
        logger = logging.getLogger(LOGGER_NAME)
        self.addCleanup(logger.removeHandler, second)

        self.assertNotIn(first, logger.handlers)
        log_event("run.started", tasks=0)
        self.assertEqual(len([line for line in stream.getvalue().splitlines() if line.strip()]), 1)


if __name__ == "__main__":
    unittest.main()
