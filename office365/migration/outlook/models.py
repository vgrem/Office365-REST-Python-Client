"""Mail export model — the options, the Graph projection, and the per-message record.

An exported message is two files: the RFC 822 bytes (``.eml``) and a JSON sidecar
carrying what MIME does not (Graph ids, categories, read state, conversation).
This module owns the sidecar's shape and the naming convention that makes a
re-run land on the same paths.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from office365.runtime.converters.scalars import iso_or_none

#: Graph message properties an export reads (one projection, so two exports of the
#: same mailbox are comparable; ``from``/``*Recipients`` are nested but selectable).
MAIL_COLUMNS = [
    "id",
    "internetMessageId",
    "subject",
    "receivedDateTime",
    "sentDateTime",
    "lastModifiedDateTime",
    "isRead",
    "isDraft",
    "importance",
    "categories",
    "hasAttachments",
    "conversationId",
    "parentFolderId",
    "size",
    "from",
    "toRecipients",
    "ccRecipients",
]

#: Filename stem cap. Well under every platform's 255-byte name limit, and long
#: enough to keep a subject recognizable next to its date and id digest.
MAX_SLUG_LENGTH = 60

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
_RUNS = re.compile(r"-{2,}")


@dataclass
class MailExportOptions:
    """What a mailbox export includes.

    Defaults are the honest ones for a migration: the whole folder tree, drafts
    included (a draft is content a user expects to find after the move).
    """

    include_subfolders: bool = True
    include_drafts: bool = True
    #: Name of the top folder in the export tree (``None`` uses the folder's own
    #: display name). Set it to keep a stable root when the source folder is
    #: renamed between runs.
    root_name: str | None = None
    #: Extra Graph message properties to record in the sidecar (camelCase names).
    #: Read with ``message.get_property(name)``; unknown names are recorded as None.
    extra_properties: list[str] = field(default_factory=list)


def mail_slug(subject: str | None) -> str:
    """A filesystem-safe, ASCII, length-capped rendering of a subject.

    Accented characters are folded to their ASCII base (``über`` -> ``uber``)
    rather than dropped, so two subjects differing only by accents do not collide;
    separators and punctuation collapse into single dashes.
    """
    if not subject:
        return ""
    folded = unicodedata.normalize("NFKD", subject).encode("ascii", "ignore").decode("ascii")
    slug = _UNSAFE.sub("-", folded).strip("-._")
    slug = _RUNS.sub("-", slug)
    return slug[:MAX_SLUG_LENGTH].strip("-._")


def message_key(message) -> str:
    """The identity an export is keyed by: ``internetMessageId``, else the Graph id.

    ``internetMessageId`` is the header-preserved identity, stable across
    mailboxes; a draft may not have one until it is sent, and its Graph id changes
    if the draft is moved, which a re-run reports as a second copy rather than
    silently overwriting.
    """
    return message.internet_message_id or message.id or ""


def mail_dest_path(message, folder_path: str) -> str:
    """The export path for a message: ``<folder>/<date>_<slug>_<id digest>.eml``.

    Deterministic for a given message, so a re-run finds the file it wrote. The
    digest of :func:`message_key` keeps messages that share a subject and a
    timestamp — newsletters, ``RE:`` threads, ``(no subject)`` — apart.
    """
    received = message.received_date_time or message.sent_date_time
    stamp = ""
    if isinstance(received, datetime) and received != datetime.min:
        stamp = received.strftime("%Y-%m-%d")
    digest = hashlib.sha1(message_key(message).encode("utf-8")).hexdigest()[:8]
    stem = "_".join(part for part in (stamp, mail_slug(message.subject), digest) if part)
    name = f"{stem}.eml"
    return f"{folder_path}/{name}" if folder_path else name


def _address(recipient) -> str | None:
    """Render a Graph recipient as ``Name <address>`` (or whichever half exists)."""
    email_address = getattr(recipient, "emailAddress", None)
    if email_address is None:
        return None
    name, address = email_address.name, email_address.address
    if name and address:
        return f"{name} <{address}>"
    return address or name


def mail_envelope(message, folder_path: str, extra_properties: list[str] | None = None) -> dict[str, Any]:
    """The sidecar record for a message: what the MIME bytes do not carry.

    All values are JSON-safe. ``received``/``sent`` are ISO-8601 (UTC as Graph
    returns it); ``categories`` is the Outlook category list — the label set a
    Gmail-to-M365 move has to map by hand.
    """
    envelope: dict[str, Any] = {
        "graph_id": message.id,
        "internet_message_id": message.internet_message_id,
        "folder_path": folder_path,
        "subject": message.subject,
        "sender": _address(message.from_recipient),
        "to": [address for address in (_address(r) for r in message.to_recipients) if address],
        "cc": [address for address in (_address(r) for r in message.cc_recipients) if address],
        "received": iso_or_none(message.received_date_time),
        "sent": iso_or_none(message.sent_date_time),
        "is_read": message.is_read,
        "is_draft": message.is_draft,
        "importance": message.importance,
        "categories": list(message.get_property("categories") or []),
        "has_attachments": message.has_attachments,
        "conversation_id": message.conversation_id,
        "parent_folder_id": message.parent_folder_id,
        "size_bytes": message.get_property("size"),
        "eml_path": mail_dest_path(message, folder_path),
    }
    for name in extra_properties or []:
        envelope[name] = message.get_property(name)
    return envelope


__all__ = [
    "MAIL_COLUMNS",
    "MAX_SLUG_LENGTH",
    "MailExportOptions",
    "mail_dest_path",
    "mail_envelope",
    "mail_slug",
    "message_key",
]
