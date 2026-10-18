"""Mail import adapters — an EML tree as the migration source, a mailbox as the target.

The other half of :mod:`office365.migration.outlook.adapters`: that module turns a
mailbox into a portable ``.eml`` tree, this one puts the tree into a mailbox::

    from office365.migration import MigrationJob
    from office365.migration.outlook import EmlTreeSource, MailboxTarget

    inbox = client.me.mail_folders["inbox"].get().execute_query()
    job = MigrationJob(EmlTreeSource("./mailbox-export"), MailboxTarget(inbox))
    job.plan()
    job.run()
    print(job.verify().summary())

The mailbox is written through Graph's MIME import (``POST <folder>/messages`` with
a base64 RFC 822 body), so attachments, encodings and nested bodies need no
translation. Three things that import cannot carry over, all of them Exchange's
choice rather than the adapter's:

* **An imported message is a draft.** Graph creates it with ``isDraft: true`` and
  ignores a PATCH that tries to clear it; only a real delivery (Exchange migration
  service, IMAP ``APPEND``) produces a non-draft.
* **``receivedDateTime`` is the import time.** The original date survives in the
  message's ``Date`` header, which Graph exposes as ``sentDateTime``.
* **Timestamps are not restorable**, so ``preserve_timestamps`` is refused up front
  by the runner instead of being silently dropped.

Content verification still works, because :func:`~office365.migration.outlook.models.mime_digest`
compares what a message *says* rather than the bytes Exchange re-serialized.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Iterable, cast

from office365.migration.adapters import DataSource, DataTarget, MigrationProgress
from office365.migration.base import MigrationItem
from office365.migration.outlook.models import MAX_IMPORT_MIME_BYTES, MailImportOptions, mime_digest
from office365.runtime.operations import emit_progress
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery

#: Sidecar suffix — the export writes ``<stem>.json`` next to ``<stem>.eml``.
SIDECAR_SUFFIX = ".json"

#: The id properties an import needs to recognise a message it already delivered.
_ID_COLUMNS = ["id", "internetMessageId"]


def _post_as_mime(request) -> None:
    """Send the base64 MIME body as ``text/plain`` — Graph's MIME import contract."""
    request.set_header("Content-Type", "text/plain")


class EmlTreeSource(DataSource):
    """Reads an exported ``.eml`` tree back as migration items.

    Each item's envelope is the JSON sidecar the export wrote beside the message, so
    folder names, categories and read state survive into the import plan.
    """

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._items: dict[str, MigrationItem] = {}

    @property
    def root(self) -> Path:
        return self._root

    def label(self) -> str:
        return f"eml:{self._root}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        if not self._root.is_dir():
            raise FileNotFoundError(f"{self._root} is not a directory of exported .eml files")
        items: list[MigrationItem] = []
        for path in sorted(self._root.rglob("*.eml")):
            item = self._item(path)
            self._items[item.dest_path] = item
            items.append(item)
            emit_progress(progress, done=len(items), stage="planning", items=[item])
        return items

    def _item(self, path: Path) -> MigrationItem:
        dest = path.relative_to(self._root).as_posix()
        envelope = self._sidecar(path)
        received = envelope.get("received")
        created = received or envelope.get("sent")
        return MigrationItem(
            source_path=dest,
            dest_path=dest,
            size_bytes=path.stat().st_size,
            item_type="file",
            modified=envelope.get("received") or envelope.get("sent"),
            created=created,
            source_id=envelope.get("internet_message_id") or envelope.get("graph_id"),
            metadata=envelope or None,
        )

    def _sidecar(self, path: Path) -> dict[str, Any]:
        sidecar = path.with_suffix(SIDECAR_SUFFIX)
        if not sidecar.exists():
            return {}
        return json.loads(sidecar.read_text(encoding="utf-8"))

    def _path(self, item: MigrationItem) -> Path:
        path = self._root / item.dest_path
        if self._root.resolve() not in path.resolve().parents:
            raise ValueError(f"{item.dest_path!r} escapes the export tree")
        return path

    def read(self, item: MigrationItem) -> bytes:
        """The message's RFC 822 bytes."""
        return self._path(item).read_bytes()

    def checksum(self, item: MigrationItem) -> str:
        return mime_digest(self.read(item))


class MailboxTarget(DataTarget):
    """Writes RFC 822 messages into a mailbox folder, creating the folder chain.

    The target folder is the import root: a source directory path becomes a chain of
    child folders under it, using the exported ``folder_display_path`` names so a
    folder called ``All Mail`` does not come back as ``All-Mail``.
    """

    def __init__(self, folder, options: MailImportOptions | None = None) -> None:
        self._root = folder
        self._options = options or MailImportOptions()
        self._folders: dict[str, Any] = {}  # source directory path -> Graph folder
        self._delivered: dict[str, dict[str, Any]] = {}  # directory -> internetMessageId -> message
        self._present: dict[str, Any] = {}  # dest path -> Graph message

    @property
    def root(self):
        return self._root

    def label(self) -> str:
        name = getattr(self._root, "display_name", None) or getattr(self._root, "id", "mailbox")
        return f"mailbox:{name}"

    # -- folders ---------------------------------------------------------------

    def _names(self, item: MigrationItem) -> tuple[str, list[str]]:
        """The source directory and the folder names to create for it.

        The export tree's first directory *is* the source mailbox folder the export
        started at, and the target folder plays that role on the way in — so it is
        dropped rather than recreated as a child of itself. Everything below it is a
        real subfolder, named from the exported ``folder_display_path`` (which keeps
        ``All Mail`` from coming back as ``All-Mail``).
        """
        directory, _, _ = item.dest_path.rpartition("/")
        segments = [segment for segment in directory.split("/") if segment][1:]
        display = str((item.metadata or {}).get("folder_display_path") or "")
        names = [name for name in display.split("/") if name]
        if len(names) == len(segments) + 1:  # the display path still carries the root
            names = names[1:]
        if len(names) != len(segments):
            names = segments
        if self._options.root_name:
            names = [self._options.root_name, *names]
        return directory, names

    def _folder(self, item: MigrationItem):
        directory, names = self._names(item)
        folder = self._folders.get(directory)
        if folder is None:
            folder = self._root
            for name in names:
                folder = folder.child_folders.ensure(name).execute_query()
            self._folders[directory] = folder
        return directory, folder

    # -- target contract -------------------------------------------------------

    def exists(self, item: MigrationItem) -> bool:
        """Whether this message was already delivered to its folder.

        Keyed by ``internetMessageId`` within the folder, because Exchange happily
        accepts the same Message-ID twice — a resume has to recognise its own work
        or it imports every message again.
        """
        if item.dest_path in self._present:
            return True
        directory, folder = self._folder(item)
        key = (item.metadata or {}).get("internet_message_id") or (item.metadata or {}).get("graph_id")
        if not key:
            return False
        delivered = self._delivered.get(directory)
        if delivered is None:
            messages = folder.messages.select(_ID_COLUMNS).get_all().execute_query()
            delivered = {message.internet_message_id: message for message in messages if message.internet_message_id}
            self._delivered[directory] = delivered
        message = delivered.get(key)
        if message is None:
            return False
        self._present[item.dest_path] = message
        return True

    def write(self, item: MigrationItem, payload: Any) -> None:
        """Create the message from its RFC 822 bytes, then replay the envelope flags."""
        data = payload if isinstance(payload, bytes) else bytes(payload)
        if len(data) > MAX_IMPORT_MIME_BYTES:
            raise ValueError(
                f"{item.dest_path}: {len(data)} bytes exceeds the {MAX_IMPORT_MIME_BYTES} byte MIME import limit "
                "(a larger message needs an upload session, which this target does not use)"
            )
        directory, folder = self._folder(item)
        collection = folder.messages
        message = collection.create_typed_object()
        collection.add_child(message)
        # The query builder passes raw bytes through untouched; the JSON serializer
        # would otherwise expect a ClientObject/dict for the parameters.
        query = CreateEntityQuery(collection, cast("Any", base64.b64encode(data)), message)
        query.before_execute(_post_as_mime)
        collection.context.add_query(query)
        collection.context.execute_query()
        self._present[item.dest_path] = message
        self._delivered.setdefault(directory, {})[message.internet_message_id] = message
        self._replay(message, collection, item.metadata or {})

    def list_paths(self) -> Iterable[str]:
        """The destination paths this target has delivered or recognised.

        A mailbox cannot be enumerated into export paths cheaply, so extras are not
        reported: presence verification covers what the plan expects.
        """
        return sorted(self._present)

    def checksum(self, item: MigrationItem) -> str:
        """Content fingerprint of the message as the mailbox returns it."""
        message = self._present.get(item.dest_path)
        if message is None:
            return ""
        return mime_digest(message.get_content().execute_query().value)

    # -- envelope replay -------------------------------------------------------

    def _replay(self, message, collection, envelope: dict[str, Any]) -> None:
        """Re-apply the flags Exchange does not take from the MIME bytes (one PATCH).

        The PATCH addresses the message through a *stub* carrying only the changed
        properties: patching the imported message object itself would resend the whole
        property bag the create response returned, and Graph rejects that (a MIME
        import reports its attachments, and a message cannot carry an abstract
        ``microsoft.graph.attachment``: ``UnprocessableType``).
        """
        properties: dict[str, Any] = {}
        if self._options.restore_read_state and envelope.get("is_read") is False:
            properties["isRead"] = False
        if self._options.restore_categories:
            categories = [category for category in envelope.get("categories") or [] if category]
            if categories:
                properties["categories"] = categories
        importance = envelope.get("importance")
        if importance and importance != "normal":
            properties["importance"] = importance
        if not properties:
            return
        stub = type(message)(message.context, EntityPath(message.id, collection.resource_path))
        for name, value in properties.items():
            stub.set_property(name, value)
        stub.update().execute_query()


__all__ = ["EmlTreeSource", "MailboxTarget", "SIDECAR_SUFFIX"]
