"""Mail export model — the options, the Graph projection, and the per-message record.

An exported message is two files: the RFC 822 bytes (``.eml``) and a JSON sidecar
carrying what MIME does not (Graph ids, categories, read state, conversation).
This module owns the sidecar's shape and the naming convention that makes a
re-run land on the same paths.
"""

from __future__ import annotations

import email
import email.policy
import email.utils
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, cast

from office365.runtime.converters.scalars import iso_or_none

#: Graph message properties an export reads (one projection, so two exports of the
#: same mailbox are comparable; ``from``/``*Recipients`` are nested but selectable).
#: ``size`` is *not* here: the Exchange-backed endpoint rejects it as a ``$select``
#: column (``Could not find a property named 'size' on type Microsoft.OutlookServices.Message``),
#: so a message's byte count is only known once its MIME is fetched.
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


#: Graph caps a MIME import request at 4 MB (the base64 body is the payload), so
#: a larger message has to go through an upload session instead.
MAX_IMPORT_MIME_BYTES = 4 * 1024 * 1024


@dataclass
class MailImportOptions:
    """What a mailbox import restores beyond the MIME bytes.

    Flag replay costs one extra PATCH per message, and only when the value Graph
    chose differs from the exported one, so the defaults are on.
    """

    #: Re-apply the exported read state. Graph marks an imported message read, so
    #: this only writes when the export says unread.
    restore_read_state: bool = True
    #: Re-apply the exported Outlook categories (the label set a Gmail move maps
    #: onto by hand).
    restore_categories: bool = True
    #: Import everything under this folder, created when absent (``None`` imports
    #: straight into the target folder).
    root_name: str | None = None


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


#: The prefix Exchange prepends to an imported HTML body. It restates the charset
#: the MIME headers already carry, so it is serialization, not content.
_EXCHANGE_HTML_PREFIX = re.compile(rb'^<meta http-equiv="Content-Type" content="[^"]*">')


def _canonical_date(value: str | None) -> str | None:
    """A ``Date`` header as ISO-8601, so ``04 Mar`` and ``4 Mar`` compare equal."""
    if not value:
        return None
    try:
        return email.utils.parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value


def _canonical_addresses(value: str | None) -> list[list[str]]:
    """An address header as ``[name, address]`` pairs (``[]`` when absent)."""
    if not value:
        return []
    return [[name, address] for name, address in email.utils.getaddresses([value])]


def _canonical_mime(data: bytes) -> dict[str, Any] | None:
    """The parts of a message that survive a round trip through Exchange.

    Exchange re-serializes an imported message: it drops the per-part
    ``MIME-Version`` headers, reflows ``Content-Type`` parameters, rewrites
    ``Date`` into its own spelling and prepends a ``<meta http-equiv=...>`` tag to
    an HTML body. None of that changes what the message says, so the fingerprint
    is built from decoded leaf payloads and semantic headers instead of bytes.
    """
    if not data:
        return None
    try:
        message = email.message_from_bytes(data, policy=email.policy.SMTP)
        leaves = []
        for part in message.walk():
            if part.is_multipart():
                continue
            payload = cast("bytes", part.get_payload(decode=True) or b"")
            if part.get_content_type() == "text/html":
                payload = _EXCHANGE_HTML_PREFIX.sub(b"", payload, count=1)
            leaves.append([part.get_content_type(), part.get_filename(), hashlib.sha256(payload).hexdigest()])
    except Exception:  # noqa: BLE001 — an unparsable message has no comparable content
        return None
    return {
        "subject": message.get("Subject"),
        "message_id": message.get("Message-ID"),
        "date": _canonical_date(message.get("Date")),
        "from": _canonical_addresses(message.get("From")),
        "to": _canonical_addresses(message.get("To")),
        "cc": _canonical_addresses(message.get("Cc")),
        "parts": leaves,
    }


def mime_digest(data: bytes) -> str:
    """A content fingerprint of an RFC 822 message that survives re-serialization.

    A byte checksum cannot verify a mailbox round trip: the same message comes
    back from Graph with different bytes (see :func:`_canonical_mime`). This
    digests what the message *says* — headers and decoded bodies, attachments
    included — so an imported copy can be compared with the ``.eml`` it came from.

    Returns an empty string for an unparsable message, which verification reports
    as unverifiable rather than as a mismatch.
    """
    canonical = _canonical_mime(data)
    if canonical is None:
        return ""
    return hashlib.sha256(json.dumps(canonical, sort_keys=True).encode("utf-8")).hexdigest()


def _address(recipient) -> str | None:
    """Render a Graph recipient as ``Name <address>`` (or whichever half exists)."""
    email_address = getattr(recipient, "emailAddress", None)
    if email_address is None:
        return None
    name, address = email_address.name, email_address.address
    if name and address:
        return f"{name} <{address}>"
    return address or name


def mail_envelope(
    message,
    folder_path: str,
    extra_properties: list[str] | None = None,
    display_path: str | None = None,
) -> dict[str, Any]:
    """The sidecar record for a message: what the MIME bytes do not carry.

    All values are JSON-safe. ``received``/``sent`` are ISO-8601 (UTC as Graph
    returns it); ``categories`` is the Outlook category list — the label set a
    Gmail-to-M365 move has to map by hand. ``folder_path`` is the slug path used
    for file names; ``folder_display_path`` is the real folder chain, which an
    import needs to recreate the folders with the names the user knows.
    """
    envelope: dict[str, Any] = {
        "graph_id": message.id,
        "internet_message_id": message.internet_message_id,
        "folder_path": folder_path,
        "folder_display_path": display_path or folder_path,
        "subject": message.subject,
        "sender": _address(message.from_recipient),
        "to": [address for address in (_address(r) for r in message.to_recipients) if address],
        "cc": [address for address in (_address(r) for r in message.cc_recipients) if address],
        "received": iso_or_none(message.received_date_time),
        "sent": iso_or_none(message.sent_date_time),
        "is_read": message.is_read,
        "is_draft": message.is_draft,
        "importance": message.importance,
        "categories": list(message.categories or []),
        "has_attachments": message.has_attachments,
        "conversation_id": message.conversation_id,
        "parent_folder_id": message.parent_folder_id,
        "eml_path": mail_dest_path(message, folder_path),
    }
    for name in extra_properties or []:
        envelope[name] = message.get_property(name)
    return envelope


__all__ = [
    "MAIL_COLUMNS",
    "MAX_IMPORT_MIME_BYTES",
    "MAX_SLUG_LENGTH",
    "MailExportOptions",
    "MailImportOptions",
    "mail_dest_path",
    "mail_envelope",
    "mail_slug",
    "message_key",
    "mime_digest",
]
