"""Mail export adapters — a mailbox folder as a migration source, EML tree as the target.

Plug the core :class:`~office365.migration.job.MigrationJob` into Outlook mail::

    from office365.migration import MigrationJob
    from office365.migration.outlook import MailExportTarget, MailExportOptions, MailFolderSource

    folder = client.me.mail_folders["inbox"].get().execute_query()
    job = MigrationJob(MailFolderSource(folder), MailExportTarget("./mailbox-export"))
    job.plan()
    job.run()
    print(job.verify().summary())

Export layout (target convention)::

    <root>/<folder>/<YYYY-MM-DD>_<subject-slug>_<id-digest>.eml   RFC 822 bytes
    <root>/<folder>/<same stem>.json                              sidecar record
    <root>/manifest.jsonl                                         one sidecar per line

The ``.eml`` is the portable artefact: it opens in Outlook, Thunderbird, macOS
Mail, and any IMAP server accepts it as an ``APPEND``. Everything MIME cannot
carry (Graph ids, read state, categories, conversation id) lives in the sidecar,
which is also what a later import reads to restore them.

Two honest limits: attachments ride **inside** the MIME payload (so they are not
separate manifest items), and the MIME body is fetched per message — the export
does not batch those reads (``Message.get_content`` is batchable since 3.3.0, so a
reader that batches them is a tuning step, not a redesign).
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from office365.migration.adapters import DataSource, DataTarget, MigrationProgress
from office365.migration.base import MigrationItem
from office365.migration.outlook.models import (
    MAIL_COLUMNS,
    MailExportOptions,
    mail_dest_path,
    mail_envelope,
    mail_slug,
)
from office365.runtime.converters.scalars import iso_or_none
from office365.runtime.operations import emit_progress

#: The index file a target writes at ``commit()`` (one JSON record per line).
MANIFEST_NAME = "manifest.jsonl"


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


class MailFolderSource(DataSource):
    """Enumerates a Graph mail folder (recursively) as one item per message.

    Each item carries its envelope in ``metadata``, so the export's index is
    written from the manifest itself — no second pass over the mailbox.
    """

    def __init__(self, folder, options: MailExportOptions | None = None) -> None:
        self._folder = folder
        self._options = options or MailExportOptions()
        self._messages: dict[str, Any] = {}  # dest path -> message handle
        self._enumerated = False

    def label(self) -> str:
        name = self._options.root_name or getattr(self._folder, "display_name", None) or self._folder.id
        return f"mail:{name}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        root = self._options.root_name or mail_slug(getattr(self._folder, "display_name", None)) or "mailbox"
        items: list[MigrationItem] = []
        self._collect(self._folder, root, items, progress)
        self._enumerated = True
        return items

    def _collect(self, folder, path: str, items: list[MigrationItem], progress) -> None:
        for message in folder.messages.select(MAIL_COLUMNS).get_all().execute_query():
            is_draft = bool(message.is_draft)
            if is_draft and not self._options.include_drafts:
                continue
            item = self._item(message, path)
            self._messages[item.dest_path] = message
            items.append(item)
            emit_progress(progress, done=len(items), stage="planning", items=[item])
        if not self._options.include_subfolders:
            return
        for child in folder.child_folders.get().execute_query():
            name = mail_slug(getattr(child, "display_name", None)) or str(child.id)
            self._collect(child, f"{path}/{name}", items, progress)

    def _item(self, message, path: str) -> MigrationItem:
        received = message.received_date_time
        modified = message.get_property("lastModifiedDateTime") or received
        dest = mail_dest_path(message, path)
        return MigrationItem(
            source_path=dest,
            dest_path=dest,
            size_bytes=int(message.get_property("size") or 0),
            item_type="file",
            modified=iso_or_none(modified) if isinstance(modified, datetime) else None,
            created=iso_or_none(received),
            source_id=message.internet_message_id or message.id,
            metadata=mail_envelope(message, path, self._options.extra_properties),
        )

    def _handle(self, item: MigrationItem):
        """The message for an item, enumerating once if the plan came from disk."""
        message = self._messages.get(item.dest_path)
        if message is None and not self._enumerated:
            self.list_items()
            message = self._messages.get(item.dest_path)
        if message is None:
            raise KeyError(f"{item.dest_path!r} was not enumerated by this source — re-plan the job")
        return message

    def read(self, item: MigrationItem) -> bytes:
        """The message's RFC 822 bytes (``GET /messages/{id}/$value``)."""
        return self._handle(item).get_content().execute_query().value

    def checksum(self, item: MigrationItem) -> str:
        return _md5(self.read(item))


class MailExportTarget(DataTarget):
    """Writes a portable EML tree: one ``.eml`` plus one JSON sidecar per message."""

    def __init__(self, root: str | Path, write_manifest: bool = True) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._write_manifest = write_manifest

    @property
    def root(self) -> Path:
        return self._root

    def label(self) -> str:
        return str(self._root)

    def _path(self, item: MigrationItem) -> Path:
        return self._root / item.dest_path

    def _sidecar(self, item: MigrationItem) -> Path:
        return self._path(item).with_suffix(".json")

    def exists(self, item: MigrationItem) -> bool:
        return self._path(item).exists()

    def write(self, item: MigrationItem, payload: Any) -> None:
        path = self._path(item)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = payload if isinstance(payload, bytes) else bytes(payload)
        path.write_bytes(data)
        envelope = dict(item.metadata or {})
        envelope.setdefault("eml_path", item.dest_path)
        envelope.setdefault("source_id", item.source_id)
        envelope["size_bytes"] = len(data)
        self._sidecar(item).write_text(json.dumps(envelope, indent=2, default=str), encoding="utf-8")

    def list_paths(self) -> Iterable[str]:
        """Every ``.eml`` under the root (sidecars and the index are not content)."""
        return (p.relative_to(self._root).as_posix() for p in sorted(self._root.rglob("*.eml")))

    def checksum(self, item: MigrationItem) -> str:
        return _md5(self._path(item).read_bytes())

    def apply_timestamps(self, item: MigrationItem) -> None:
        """Stamp the ``.eml`` with the message's last-modified time (``preserve_timestamps``).

        A mail export has no per-item metadata the filesystem honours, so the file
        mtime is the only timestamp it can really preserve; the sidecar keeps the
        original values either way.
        """
        stamp = item.modified
        path = self._path(item)
        if not stamp or not path.exists():
            return
        parsed = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        seconds = parsed.timestamp()
        os.utime(path, (seconds, seconds))

    def read_metadata(self, item: MigrationItem) -> dict[str, Any] | None:
        """The sidecar record (what the export recorded about this message)."""
        sidecar = self._sidecar(item)
        return json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else None

    def commit(self, options=None) -> None:
        """Write ``manifest.jsonl`` — read back from the sidecars, so a resumed run's index is complete."""
        if not self._write_manifest:
            return
        records = []
        for sidecar in sorted(self._root.rglob("*.json")):
            records.append(json.loads(sidecar.read_text(encoding="utf-8")))
        lines = "".join(json.dumps(record, default=str) + "\n" for record in records)
        (self._root / MANIFEST_NAME).write_text(lines, encoding="utf-8")

    def close(self) -> None:
        pass


__all__ = ["MANIFEST_NAME", "MailExportTarget", "MailFolderSource"]
