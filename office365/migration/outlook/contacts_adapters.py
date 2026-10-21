"""Contact adapters — a Graph contact folder as a source, a vCard tree as a target, and back.

Export a contact folder::

    from office365.migration import MigrationJob
    from office365.migration.outlook import ContactExportOptions, ContactSource, VcfExportTarget

    folder = client.me.contact_folders.get().execute_query()[0]
    job = MigrationJob(ContactSource(folder), VcfExportTarget("./contacts-export"))
    job.plan()
    job.run()
    print(job.verify().summary())

Import it into another contact folder::

    from office365.migration.outlook import ContactImportOptions, ContactTarget, VcfTreeSource

    options = ContactImportOptions()
    folder = client.me.contact_folders.add("Imported").execute_query()
    job = MigrationJob(VcfTreeSource("./contacts-export", options), ContactTarget(folder, options))
    job.plan()
    job.run()
    print(job.verify().summary())

Pass the *same* options object to both sides of an import: the source computes the
content digest of what the target promises to restore.

Export layout (the same convention the mail and calendar exports use)::

    <root>/<folder>/<name-slug>_<id-digest>.vcf   vCard 3.0 document
    <root>/<folder>/<same stem>.json             sidecar record
    <root>/manifest.jsonl                        one sidecar per line

Four honest limits, all measured against Exchange:

* **A photo is not exported.** The ``contact`` entity exposes no ``hasPhoto`` column
  on this endpoint, so finding out costs one ``GET /photo`` that 404s
  (``ErrorItemNotFound``) per contact without one; on a folder of thousands that is
  a request per contact for the minority that have an image. Declared, not silent.
* **Timestamps are not restorable.** Exchange stamps a created contact with the
  import time and offers no field to set otherwise, so ``created``/``modified`` live
  in the sidecar as a record and nowhere else.
* **A birthday is normalised to a fixed time of day** (``11:59``), so an import is
  verified by the *date* it falls on rather than the instant — which is all a
  birthday ever meant.
* **A contact has no ``transactionId``**, unlike a message, so concurrency is handled
  by the target's own index (display name plus first address) instead of by the
  service refusing a second write. Two runs that overlap can therefore still import
  the same contact twice.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from office365.migration.adapters import DataSource, DataTarget, MigrationProgress
from office365.migration.base import MigrationItem
from office365.migration.outlook.adapters import SidecarTreeTarget
from office365.migration.outlook.contacts_models import (
    CONTACT_COLUMNS,
    ContactExportOptions,
    ContactImportOptions,
    contact_create_payload,
    contact_dedup_key,
    contact_dest_path,
    contact_digest,
    contact_envelope,
    contact_key,
    contact_vcard,
)
from office365.migration.outlook.eml_import import SIDECAR_SUFFIX
from office365.migration.outlook.fidelity import CONTACTS_EXPORT_DIMENSIONS, CONTACTS_IMPORT_DIMENSIONS
from office365.migration.outlook.models import mail_slug
from office365.outlook.contacts.contact import Contact
from office365.outlook.contacts.folders.collection import ContactFolderCollection
from office365.runtime.converters.scalars import iso_or_none
from office365.runtime.operations import emit_progress
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery

#: The properties an import reads back to recognise a contact it already created.
#: Identity and the two fields a dedupe checks; narrower than ``CONTACT_COLUMNS``
#: on purpose — it runs per item. Spelled through the model so a rename cannot
#: leave it stale.
_EXISTING_COLUMNS = [Contact.wire_name(attr) for attr in ("id", "display_name", "email_addresses")]


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _ensure_child(folder, name: str):
    """An idempotent child folder under ``folder``.

    ``ContactFolder.child_folders`` is the generated plain ``EntityCollection``, which
    has no ``ensure``; the specialised collection knows how to look the name up before
    creating it, so a re-run does not leave a duplicate folder behind.
    """
    collection = folder.properties.get("childFolders")
    if collection is None or not hasattr(collection, "ensure"):
        collection = ContactFolderCollection(folder.context, ResourcePath("childFolders", folder.resource_path))
    return collection.ensure(name).execute_query()


class ContactSource(DataSource):
    """Enumerates a Graph contact folder (and its children) as one item per contact.

    Each item carries its sidecar record in ``metadata``, so the export's index is
    written from the manifest itself — no second pass over the folder.
    """

    #: What a contact export preserves; see ``outlook.fidelity``.
    fidelity_dimensions = CONTACTS_EXPORT_DIMENSIONS

    def __init__(self, folder, options: ContactExportOptions | None = None) -> None:
        self._folder = folder
        self._options = options or ContactExportOptions()
        self._contacts: dict[str, Any] = {}  # dest path -> contact handle
        self._enumerated = False

    def label(self) -> str:
        name = getattr(self._folder, "display_name", None) or getattr(self._folder, "id", "contacts")
        return f"contacts:{name}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        path = self._options.root_name or mail_slug(getattr(self._folder, "display_name", None)) or "contacts"
        display = getattr(self._folder, "display_name", None) or path
        items: list[MigrationItem] = []
        self._collect(self._folder, path, display, items, progress)
        self._enumerated = True
        return items

    def _collect(self, folder, path: str, display: str, items: list[MigrationItem], progress) -> None:
        for contact in folder.contacts.select(CONTACT_COLUMNS).get_all().execute_query():
            item = self._item(contact, path, display)
            self._contacts[item.dest_path] = contact
            items.append(item)
            emit_progress(progress, done=len(items), stage="planning", items=[item])
        if not self._options.include_subfolders:
            return
        for child in folder.child_folders.get().execute_query():
            name = mail_slug(getattr(child, "display_name", None)) or str(child.id)
            child_display = getattr(child, "display_name", None) or name
            self._collect(child, f"{path}/{name}", f"{display}/{child_display}", items, progress)

    def _item(self, contact, path: str, display: str) -> MigrationItem:
        dest = contact_dest_path(contact, path)
        modified = contact.last_modified_datetime
        created = contact.created_datetime
        return MigrationItem(
            source_path=dest,
            dest_path=dest,
            # A contact has no byte size until its ``.vcf`` is rendered; ``read()`` fills it.
            size_bytes=0,
            item_type="contact",
            modified=iso_or_none(modified),
            created=iso_or_none(created),
            source_id=contact_key(contact),
            metadata=contact_envelope(contact, path, self._options.extra_properties, display),
        )

    def _handle(self, item: MigrationItem):
        """The contact for an item, enumerating once if the plan came from disk."""
        contact = self._contacts.get(item.dest_path)
        if contact is None and not self._enumerated:
            self.list_items()
            contact = self._contacts.get(item.dest_path)
        if contact is None:
            raise KeyError(f"{item.dest_path!r} was not enumerated by this source — re-plan the job")
        return contact

    def read(self, item: MigrationItem) -> bytes:
        """The contact's vCard document, rendered from the record in ``metadata``."""
        data = contact_vcard(item.metadata or {})
        item.size_bytes = len(data)
        return data

    def checksum(self, item: MigrationItem) -> str:
        """The ``.vcf`` bytes — this export renders them itself, so equality is fair."""
        return _md5(self.read(item))


class VcfExportTarget(SidecarTreeTarget):
    """Writes a portable vCard tree: one ``.vcf`` plus one JSON sidecar per contact."""

    fidelity_dimensions = CONTACTS_EXPORT_DIMENSIONS
    content_suffix = ".vcf"
    payload_key = "vcf_path"


class VcfTreeSource(DataSource):
    """Reads an exported contact tree back as migration items.

    The ``.vcf`` is the payload (what another client opens); the JSON sidecar is the
    record the import replays, and it is **required** — a vCard cannot carry the
    office fields, the address components or the categories without a lossy mapping,
    and reading a contact back out of one would invent an import nobody verified.
    """

    #: What a contact import preserves; see ``outlook.fidelity``.
    fidelity_dimensions = CONTACTS_IMPORT_DIMENSIONS

    def __init__(self, root: str | Path, options: ContactImportOptions | None = None) -> None:
        self._root = Path(root)
        self._options = options or ContactImportOptions()
        self._items: dict[str, MigrationItem] = {}

    @property
    def root(self) -> Path:
        return self._root

    def label(self) -> str:
        return f"vcf:{self._root}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        if not self._root.is_dir():
            raise FileNotFoundError(f"{self._root} is not a directory of exported .vcf files")
        items: list[MigrationItem] = []
        for path in sorted(self._root.rglob("*.vcf")):
            item = self._item(path)
            self._items[item.dest_path] = item
            items.append(item)
            emit_progress(progress, done=len(items), stage="planning", items=[item])
        return items

    def _item(self, path: Path) -> MigrationItem:
        dest = path.relative_to(self._root).as_posix()
        envelope = self._sidecar(path)
        return MigrationItem(
            source_path=dest,
            dest_path=dest,
            size_bytes=path.stat().st_size,
            item_type="contact",
            modified=envelope.get("lastModifiedDateTime"),
            created=envelope.get("createdDateTime") or envelope.get("lastModifiedDateTime"),
            source_id=envelope.get("id"),
            metadata=envelope,
        )

    def _sidecar(self, path: Path) -> dict[str, Any]:
        sidecar = path.with_suffix(SIDECAR_SUFFIX)
        if not sidecar.exists():
            raise FileNotFoundError(
                f"{sidecar} is missing: the sidecar is the import contract (a vCard cannot carry the office fields,"
                " address components and categories without loss), so the tree has to come from a contact export"
            )
        return json.loads(sidecar.read_text(encoding="utf-8"))

    def _path(self, item: MigrationItem) -> Path:
        path = self._root / item.dest_path
        if self._root.resolve() not in path.resolve().parents:
            raise ValueError(f"{item.dest_path!r} escapes the export tree")
        return path

    def read(self, item: MigrationItem) -> bytes:
        """The contact's vCard document."""
        return self._path(item).read_bytes()

    def checksum(self, item: MigrationItem) -> str:
        """The digest a contact target can also compute, not the ``.vcf`` bytes.

        The target is Exchange, which assigns the identifiers and rewrites a
        birthday's time of day, so the comparable artefact is the contact's
        restorable fields rather than the document that carried them.
        """
        return contact_digest(item.metadata or {}, self._options)


class ContactTarget(DataTarget):
    """Recreates exported contacts in a Graph contact folder.

    The source of truth is the sidecar, not the ``.vcf``: the create body is posted
    verbatim (:func:`contact_create_payload`) because ``ContactCollection.add()``
    builds its own body from four arguments and drops everything else.
    """

    fidelity_dimensions = CONTACTS_IMPORT_DIMENSIONS

    def __init__(self, folder, options: ContactImportOptions | None = None) -> None:
        self._root = folder
        self._options = options or ContactImportOptions()
        self._folders: dict[str, Any] = {}  # source directory path -> Graph folder
        self._indexed: dict[str, dict[tuple[str, str], list[Any]]] = {}  # folder id -> dedupe index
        self._claimed: dict[tuple[str, str], int] = {}
        self._present: dict[str, Any] = {}  # dest path -> created/found contact
        self._categories_dropped = 0
        #: Warnings a caller collects (the resolver convention).
        self.warnings: list[str] = []

    @property
    def root(self):
        return self._root

    def label(self) -> str:
        name = getattr(self._root, "display_name", None) or getattr(self._root, "id", "contacts")
        return f"contacts:{name}"

    # -- folders ---------------------------------------------------------------

    def _names(self, item: MigrationItem) -> tuple[str, list[str]]:
        """The source directory and the child folder names to create under the root.

        The export tree's first directory *is* the source folder the export started
        at, and the target folder plays that role on the way in — so it is dropped
        rather than recreated as a child of itself. Anything below it is a real
        subfolder, named from the exported ``folder_display_path``.
        """
        directory, _, _ = item.dest_path.rpartition("/")
        segments = [segment for segment in directory.split("/") if segment][1:]
        display = str((item.metadata or {}).get("folder_display_path") or "")
        names = [name for name in display.split("/") if name]
        if len(names) == len(segments) + 1:  # the display path still carries the root
            names = names[1:]
        if len(names) != len(segments):
            names = segments
        return directory, names

    def _folder(self, item: MigrationItem):
        directory, names = self._names(item)
        folder = self._folders.get(directory)
        if folder is None:
            folder = self._root
            for name in names:
                folder = _ensure_child(folder, name)
            self._folders[directory] = folder
        return directory, folder

    # -- target contract -------------------------------------------------------

    def exists(self, item: MigrationItem) -> bool:
        """Whether an equal contact is already in the target folder.

        Matched on display name plus first address, because nothing the source knows
        survives the create. Duplicates *at the source* are honoured: the index keeps
        a list per key and each source item claims its own entry, so two contacts with
        the same name and address are still imported twice.
        """
        if item.dest_path in self._present:
            return True
        _, folder = self._folder(item)
        key = contact_dedup_key(item.metadata or {})
        claimed = self._claimed.get(key, 0)
        index = self._folder_index(folder)
        if claimed >= len(index.get(key) or []):
            return False
        self._claimed[key] = claimed + 1
        self._present[item.dest_path] = index[key][claimed]
        return True

    def write(self, item: MigrationItem, payload: Any) -> None:
        """Create the contact from its sidecar record.

        ``payload`` (the ``.vcf`` bytes) is deliberately unused: Graph's create body
        is the record's fields, and parsing the vCard would lose the office fields
        the export preserved precisely so this could be exact.
        """
        if item.item_type != "contact":
            raise ValueError(f"a contact folder imports contacts, not {item.item_type!r} ({item.dest_path})")
        envelope = item.metadata or {}
        try:
            body = contact_create_payload(envelope, self._options)
        except ValueError as e:
            raise ValueError(f"{item.dest_path}: {e}") from None
        _, folder = self._folder(item)
        collection = folder.contacts
        contact = collection.create_typed_object()
        collection.context.add_query(CreateEntityQuery(collection, body, contact))
        collection.context.execute_query()
        if not self._options.restore_categories and envelope.get("categories"):
            self._categories_dropped += 1
        self._present[item.dest_path] = contact
        key = contact_dedup_key(envelope)
        self._folder_index(folder).setdefault(key, []).append(contact)
        self._claimed[key] = self._claimed.get(key, 0) + 1

    def list_paths(self) -> Iterable[str]:
        """The destination paths this target has created or recognised.

        A contact folder cannot be enumerated into export paths (the paths carry the
        source's name slug and id digest), so extras are not reported: presence
        verification covers what the plan expects, and the extras are contacts the
        user already had.
        """
        return sorted(self._present)

    def checksum(self, item: MigrationItem) -> str:
        """Fingerprint of the contact as the target folder returns it."""
        contact = self._present.get(item.dest_path)
        if contact is None:
            return ""
        _, folder = self._folder(item)
        # Read a fresh object through the folder the contact lives in: re-loading the
        # created one *appends* to its collection-valued properties (``emailAddresses``,
        # the phone lists, ``categories``), so the digest would see every list twice.
        read = folder.contacts[contact.id].select(CONTACT_COLUMNS).get().execute_query()
        return contact_digest(contact_envelope(read, ""), self._options)

    def commit(self, options: Any = None) -> None:  # noqa: ARG002 — runner hook signature
        """Report once what the run deliberately did not restore."""
        if self._categories_dropped:
            self.warnings.append(
                f"categories were left off {self._categories_dropped} contact(s): "
                "ContactImportOptions(restore_categories=False) asked for that"
            )

    # -- helpers ---------------------------------------------------------------

    def _folder_index(self, folder) -> dict[tuple[str, str], list[Any]]:
        """The folder's contacts, grouped by the key an import recognises."""
        directory = getattr(folder, "id", str(folder))
        cached = self._indexed.get(directory)
        if cached is None:
            index: dict[tuple[str, str], list[Any]] = {}
            for contact in folder.contacts.select(_EXISTING_COLUMNS).get_all().execute_query():
                key = contact_dedup_key(contact.to_json())
                index.setdefault(key, []).append(contact)
            self._indexed[directory] = index
            cached = index
        return cached


__all__ = ["ContactSource", "ContactTarget", "VcfExportTarget", "VcfTreeSource"]
