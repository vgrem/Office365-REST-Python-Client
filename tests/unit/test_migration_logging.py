import json
import logging
import tempfile
import unittest
from pathlib import Path

from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget
from office365.migration.job import MigrationJob
from office365.migration.logging import (
    LOGGER_NAME,
    JsonLogFormatter,
    ProgressReporter,
    configure_json_logging,
    configure_text_logging,
    log_event,
)
from office365.migration.session import MigrationSession
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
    def test_events_are_written_as_json_lines(self):
        import io

        stream = io.StringIO()
        handler = configure_json_logging(stream)
        self.addCleanup(logging.getLogger(LOGGER_NAME).removeHandler, handler)

        log_event("job.started", "Documents", items=3)

        payload = json.loads(stream.getvalue().strip())
        self.assertEqual(payload["event"], "job.started")
        self.assertEqual(payload["items"], 3)

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

    def test_a_new_total_restarts_the_window(self):
        self.now = 4.0
        self.reporter(Progress(done=40, total=100))
        self.now = 8.0
        self.reporter(Progress(done=10, total=20))  # a second container: window restarts
        self.now = 12.0

        beat = self.reporter.flush()
        self.assertEqual(beat["done"], 10)
        self.assertEqual(beat["total"], 20)
        self.assertEqual(beat["rate"], 2.5)  # 10 done in the 4s since the restart
        self.assertEqual(beat["elapsed_seconds"], 4.0)

    def test_closing_reports_a_count_the_interval_swallowed(self):
        self.reporter(Progress(done=7, total=10))

        summary = self.reporter.close()

        self.assertEqual(len(self.beats), 1)
        self.assertEqual(self.beats[0]["done"], 7)
        self.assertEqual(summary, "Documents: 7/10 (70.0%)")

    def test_an_unknown_total_reports_no_percentage(self):
        self.now = 10.0
        self.reporter(Progress(done=30))

        beat = self.reporter.flush()

        self.assertIsNone(beat["percent"])
        self.assertIsNone(beat["eta_seconds"])
        self.assertEqual(self.reporter.summary(), "Documents: 30 3/s")

    def test_an_indeterminate_stage_clears_the_previous_total(self):
        # Structure replay is counted; pages and navigation are not. A stale total
        # would otherwise make the heartbeat claim a percentage it cannot know.
        self.reporter(Progress(done=4, total=4, stage="structure"))
        self.now = 10.0
        self.reporter(Progress(done=0, stage="pages"))

        beat = self.reporter.flush()

        self.assertEqual(beat["stage"], "pages")
        self.assertIsNone(beat["total"])
        self.assertEqual(beat["done"], 0)

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
    def test_a_job_reports_its_plan_and_its_run(self):
        handler = self.capture()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            source.mkdir()
            (source / "a.txt").write_text("alpha")
            job = MigrationJob(FileSystemSource(source), FileSystemTarget(Path(tmp) / "dst"))

            job.plan()
            job.run()

        planned = self.events(handler, "plan.completed")[0]
        self.assertEqual(planned.items, 1)  # type: ignore[attr-defined]
        started = self.events(handler, "job.started")[0]
        self.assertEqual(started.items, 1)  # type: ignore[attr-defined]
        completed = self.events(handler, "job.completed")[0]
        self.assertEqual(completed.success, 1)  # type: ignore[attr-defined]
        self.assertEqual(completed.skipped, 0)  # type: ignore[attr-defined]
        self.assertEqual(completed.phase, "completed")  # type: ignore[attr-defined]
        self.assertIsInstance(completed.duration_ms, int)  # type: ignore[attr-defined]

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

    def test_a_session_reports_its_run(self):
        handler = self.capture()

        statuses = MigrationSession().start()

        self.assertEqual(statuses, [])
        self.assertEqual(len(self.events(handler, "run.started")), 1)
        completed = self.events(handler, "run.completed")[0]
        self.assertEqual(completed.tasks, 0)  # type: ignore[attr-defined]
        self.assertEqual(completed.errors, 0)  # type: ignore[attr-defined]


class TestConfigureTextLogging(unittest.TestCase):
    def test_events_are_written_as_plain_lines(self):
        import io

        stream = io.StringIO()
        handler = configure_text_logging(stream)
        self.addCleanup(logging.getLogger(LOGGER_NAME).removeHandler, handler)

        log_event("job.failed", "library:/sites/t: denied", level=logging.WARNING, source="library:/sites/s")

        lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("WARNING"))
        self.assertIn("library:/sites/t: denied", lines[0])
        self.assertTrue(lines[0].endswith("[job.failed]"))

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
