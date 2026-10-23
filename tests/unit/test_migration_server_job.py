"""Tests for the server-side migration job (submit + progress parsing)."""

from __future__ import annotations

import asyncio
import json

from office365.migration.server_job import MigrationServerJob


class _Result:
    def __init__(self, value):
        self.value = value

    def execute_query(self):
        return self

    async def execute_query_async(self):
        return self


class _Progress:
    def __init__(self, logs, next_token):
        self.Logs = logs
        self.NextToken = next_token


class _Site:
    url = "https://contoso.sharepoint.com/sites/x"

    def __init__(self, pages=None):
        self.calls: list = []
        self._pages = list(pages or [])

    def create_migration_ingestion_job(self, **kwargs):
        self.calls.append(("ingestion", kwargs))
        return _Result("job-1")

    def create_migration_job_encrypted(self, **kwargs):
        self.calls.append(("encrypted", kwargs))
        return _Result("job-2")

    def get_migration_job_progress(self, job_id, next_token):
        self.calls.append(("progress", job_id, next_token))
        page = self._pages.pop(0) if self._pages else ([], next_token)
        return _Result(_Progress(*page))


def test_submit_and_submit_encrypted_use_the_right_methods():
    site = _Site()
    job = MigrationServerJob(site)

    assert job.submit("web", "src", "manifest") == "job-1"
    kind, kwargs = site.calls[0]
    assert kind == "ingestion"
    assert kwargs["g_web_id"] == "web"
    assert kwargs["ingestion_task_key"]

    assert job.submit_encrypted("web", "src", "manifest", b"key") == "job-2"
    kind, kwargs = site.calls[1]
    assert kind == "encrypted"
    assert kwargs["aes256_cbc_key"] == b"key"


def test_status_fn_accumulates_pages():
    pages = [
        (
            [
                json.dumps({"Event": "JobStart"}),
                json.dumps({"Event": "JobProgress", "ObjectsProcessed": "2", "TotalExpectedSPObjects": "5"}),
            ],
            "1",
        ),
        (
            [
                json.dumps(
                    {
                        "Event": "JobEnd",
                        "ObjectsProcessed": "5",
                        "TotalExpectedSPObjects": "5",
                        "TotalErrors": "0",
                    }
                )
            ],
            "2",
        ),
    ]
    status = MigrationServerJob(_Site(pages)).status_fn()

    assert status("job-1") == ("processing", 2, 5)
    assert status("job-1") == ("succeeded", 5, 5)


def test_monitor_returns_when_terminal():
    pages = [([json.dumps({"Event": "JobEnd", "TotalErrors": "0"})], "1")]
    assert MigrationServerJob(_Site(pages)).monitor("job-1", interval=0, timeout=5) == "succeeded"


def test_errors_returns_job_error_events():
    pages = [([json.dumps({"Event": "JobError", "Message": "boom"})], "1")]
    assert [e["Message"] for e in MigrationServerJob(_Site(pages)).errors("job-1")] == ["boom"]


def test_status_fn_async_accumulates_pages():
    pages = [
        (
            [
                json.dumps({"Event": "JobStart"}),
                json.dumps({"Event": "JobProgress", "ObjectsProcessed": "2", "TotalExpectedSPObjects": "5"}),
            ],
            "1",
        ),
        (
            [
                json.dumps(
                    {
                        "Event": "JobEnd",
                        "ObjectsProcessed": "5",
                        "TotalExpectedSPObjects": "5",
                        "TotalErrors": "0",
                    }
                )
            ],
            "2",
        ),
    ]
    status = MigrationServerJob(_Site(pages)).status_fn_async()

    async def _run():
        return await status("job-1"), await status("job-1")

    assert asyncio.run(_run()) == (("processing", 2, 5), ("succeeded", 5, 5))


def test_monitor_async_returns_when_terminal():
    pages = [([json.dumps({"Event": "JobEnd", "TotalErrors": "0"})], "1")]

    async def _run():
        return await MigrationServerJob(_Site(pages)).monitor_async("job-1", interval=0, timeout=5)

    assert asyncio.run(_run()) == "succeeded"


def test_errors_async_returns_job_error_events():
    pages = [([json.dumps({"Event": "JobError", "Message": "boom"})], "1")]

    async def _run():
        return await MigrationServerJob(_Site(pages)).errors_async("job-1")

    assert [e["Message"] for e in asyncio.run(_run())] == ["boom"]
