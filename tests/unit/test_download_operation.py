"""Offline tests for the high-level download API.

Covers ``Folder.download`` / ``FileCollection.download`` / ``File.download(path)``:
enumeration, relative-path layout, skip-existing, continue-and-report, progress,
and both the sync and async terminals. All I/O is served by a routing, in-memory
transport — no network.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.collection import FileCollection
from office365.sharepoint.files.file import File
from tests._scripted_transport import RoutingTransport

_SITE_URL = "https://contoso.sharepoint.com/sites/dev"
_ROOT = "/sites/dev/Shared Documents"
_NOT_FOUND = {"status": 404, "body": {"error": {"message": "missing"}}}


def _context(routes: list[tuple[str, object]]) -> tuple[ClientContext, RoutingTransport]:
    ctx = ClientContext(_SITE_URL)
    ctx.pending_request().beforeExecute.clear()
    transport = RoutingTransport(routes)
    ctx.pending_request().transport = transport
    return ctx, transport


def _add_file(ctx: ClientContext, collection: FileCollection, name: str, url: str) -> File:
    """Populate a collection with a file addressed by its server-relative URL."""
    file = File(ctx)
    collection.add_child(file)
    file.set_property("Name", name)
    file.set_property("ServerRelativeUrl", url)
    return file


def _folder(ctx: ClientContext):
    folder = ctx.web.get_folder_by_server_relative_url(_ROOT)
    folder.set_property("ServerRelativeUrl", _ROOT)
    return folder


def _loaded_collection(ctx: ClientContext) -> FileCollection:
    folder = _folder(ctx)
    return folder.files


def test_file_collection_download_writes_files(tmp_path: Path) -> None:
    ctx, _ = _context([("a.txt", b"AAA"), ("b.txt", b"BBB")])
    col = _loaded_collection(ctx)
    _add_file(ctx, col, "a.txt", f"{_ROOT}/a.txt")
    _add_file(ctx, col, "b.txt", f"{_ROOT}/b.txt")

    result = col.download(tmp_path).execute_query(concurrency=2).value

    assert result.total == 2  # noqa: PLR2004
    assert result.success == 2  # noqa: PLR2004
    assert result.errors == 0
    assert bool(result) is True
    assert (tmp_path / "a.txt").read_bytes() == b"AAA"
    assert (tmp_path / "b.txt").read_bytes() == b"BBB"
    assert sorted(result.paths) == sorted([str(tmp_path / "a.txt"), str(tmp_path / "b.txt")])


def test_download_continues_and_reports_on_error(tmp_path: Path) -> None:
    ctx, _ = _context([("a.txt", b"AAA"), ("b.txt", _NOT_FOUND)])
    col = _loaded_collection(ctx)
    _add_file(ctx, col, "a.txt", f"{_ROOT}/a.txt")
    _add_file(ctx, col, "b.txt", f"{_ROOT}/b.txt")

    result = col.download(tmp_path).execute_query(concurrency=2, max_retry=1, timeout_secs=0).value

    assert result.success == 1
    assert result.errors == 1
    assert len(result.failures) == 1
    failed_file, error = result.failures[0]
    assert failed_file.name == "b.txt"
    assert bool(result) is False
    assert (tmp_path / "a.txt").read_bytes() == b"AAA"
    assert not (tmp_path / "b.txt").exists()


def test_download_reports_global_progress(tmp_path: Path) -> None:
    ctx, _ = _context([("a.txt", b"AAA"), ("b.txt", b"BBB")])
    col = _loaded_collection(ctx)
    _add_file(ctx, col, "a.txt", f"{_ROOT}/a.txt")
    _add_file(ctx, col, "b.txt", f"{_ROOT}/b.txt")
    seen = []

    col.download(tmp_path, progress=seen.append).execute_query(concurrency=2)

    assert [p.done for p in seen] == [1, 2]
    assert seen[-1].total == 2  # noqa: PLR2004
    assert seen[-1].stage == "downloading"


def test_folder_download_preserves_relative_tree(tmp_path: Path, monkeypatch) -> None:
    ctx, _ = _context([("root.txt", b"ROOT"), ("deep.txt", b"DEEP")])
    folder = _folder(ctx)
    col = FileCollection(ctx, folder.files.resource_path, folder)
    _add_file(ctx, col, "root.txt", f"{_ROOT}/root.txt")
    _add_file(ctx, col, "deep.txt", f"{_ROOT}/sub/deep.txt")
    seen: dict = {}

    def _get_files(**kwargs):
        seen.update(kwargs)
        return col

    monkeypatch.setattr(folder, "get_files", _get_files)

    result = folder.download(tmp_path, recursive=True).execute_query(concurrency=2).value

    assert seen["recursive"] is True
    assert result.success == 2  # noqa: PLR2004
    assert (tmp_path / "root.txt").read_bytes() == b"ROOT"
    assert (tmp_path / "sub" / "deep.txt").read_bytes() == b"DEEP"


def test_file_download_path_async_and_overwrite(tmp_path: Path) -> None:
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"OLD")
    ctx, transport = _context([("a.txt", b"NEW")])
    file = File(ctx)
    file.set_property("Name", "a.txt")
    file.set_property("ServerRelativeUrl", f"{_ROOT}/a.txt")

    op = file.download(dest)
    assert op.execute_query(concurrency=2) is op
    assert op.value.skipped == 1
    assert dest.read_bytes() == b"OLD"
    assert transport.calls == []

    result = asyncio.run(file.download(dest, overwrite=True).execute_query_async(concurrency=2)).value
    assert result.success == 1
    assert dest.read_bytes() == b"NEW"


def test_download_resume_appends_missing_range(tmp_path: Path) -> None:
    ctx, transport = _context([("a.txt", {"status": 206, "body": b"world"})])
    col = _loaded_collection(ctx)
    file = _add_file(ctx, col, "a.txt", f"{_ROOT}/a.txt")
    file.set_property("Length", 10)
    (tmp_path / "a.txt").write_bytes(b"hello")

    result = col.download(tmp_path, resume=True).execute_query(concurrency=2).value

    assert result.success == 1
    assert result.skipped == 0
    assert (tmp_path / "a.txt").read_bytes() == b"helloworld"
    assert len(transport.calls) == 1
    assert transport.requests[0].headers.get("Range") == "bytes=5-"


def test_download_resume_async(tmp_path: Path) -> None:
    ctx, _ = _context([("a.txt", {"status": 206, "body": b"world"})])
    col = _loaded_collection(ctx)
    file = _add_file(ctx, col, "a.txt", f"{_ROOT}/a.txt")
    file.set_property("Length", 10)
    (tmp_path / "a.txt").write_bytes(b"hello")

    result = asyncio.run(col.download(tmp_path, resume=True).execute_query_async(concurrency=2)).value

    assert result.success == 1
    assert (tmp_path / "a.txt").read_bytes() == b"helloworld"


def test_file_download_resume_loads_length(tmp_path: Path) -> None:
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"hello")
    ctx, _ = _context(
        [
            ("$select=Length", {"d": {"Length": 10}}),
            ("/$value", {"status": 206, "body": b"world"}),
        ]
    )
    file = File(ctx)
    file.set_property("Name", "out.bin")
    file.set_property("ServerRelativeUrl", f"{_ROOT}/out.bin")

    result = file.download(dest, resume=True).execute_query(concurrency=2).value

    assert result.success == 1
    assert dest.read_bytes() == b"helloworld"
