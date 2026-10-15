"""Crash-safe JSON persistence for resumable run state.

Run state (checkpoints, watermarks, cursors) must survive a process crash at any
moment. Writing JSON in place is **not** safe: a crash mid-write leaves a
truncated file that cannot be parsed, so the next run cannot resume — the exact
failure the checkpoint exists to prevent.

:func:`atomic_write_json` writes to a sibling temporary file, flushes it to disk,
then atomically replaces the target with :func:`os.replace` (atomic on POSIX and
Windows). A concurrent reader therefore always sees either the old contents or
the complete new contents, never a partial write.
"""

from __future__ import annotations

import json
import os
import tempfile
from os import PathLike
from pathlib import Path
from typing import Any, Union

#: Anything accepted as a filesystem path.
PathLikeType = Union[str, PathLike]


def atomic_write_json(path: PathLikeType, payload: Any, *, indent: int = 2) -> None:
    """Serialize ``payload`` to ``path`` atomically and durably.

    The payload is written to a uniquely-named temporary file next to ``path``,
    flushed and ``fsync``-ed, then moved onto ``path`` with :func:`os.replace`.
    On POSIX the containing directory is also ``fsync``-ed so the rename itself
    survives a crash. A failure while writing removes the temporary file and
    leaves ``path`` untouched. Missing parent directories are created.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=indent)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    _fsync_directory(target.parent)


def read_json(path: PathLikeType) -> Any:
    """Parse a JSON value previously written by :func:`atomic_write_json`."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _fsync_directory(directory: Path) -> None:
    """Best-effort ``fsync`` of a directory (POSIX only; a no-op elsewhere)."""
    if not hasattr(os, "O_DIRECTORY"):
        return
    try:
        fd = os.open(directory, os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)
