"""What an Outlook migration preserves — the fidelity matrix each pair declares.

The engine's fidelity matrix (:func:`office365.migration.fidelity.describe_fidelity`)
started life as a probe of the SharePoint adapters, so its fourteen dimensions name
SharePoint concepts: views, navigation, site settings, sharing links, content types.
A mailbox has none of those, and printing them for a mail export said both too much
(`views=unsupported`, which nobody asked) and too little (`content=delivered`, with a
note about *list-item* attachments).

So a product declares its own table instead. :data:`MAIL_EXPORT_DIMENSIONS` and its
three siblings are plain dicts of ``dimension → (status, reason)``; the source adapter
carries one as ``fidelity_dimensions`` and the engine reports it verbatim. The four
tables are per direction on purpose — the export keeps a message's dates in the
sidecar while the import cannot set `receivedDateTime` at all — so a single table
would have to be vague about both.

Nothing here probes an adapter: a declared matrix is a claim, and
``tests/unit/test_migration_fidelity.py`` holds it to what the adapters do.
"""

from __future__ import annotations

from typing import Dict, Tuple

from office365.migration.fidelity import FidelityStatus

__all__ = [
    "CALENDAR_EXPORT_DIMENSIONS",
    "CALENDAR_IMPORT_DIMENSIONS",
    "MAIL_EXPORT_DIMENSIONS",
    "MAIL_IMPORT_DIMENSIONS",
]

#: One dimension's status and the reason for it.
Dimension = Tuple[FidelityStatus, str]

_NOT_READ_ACLS = "a folder's delegation is a tenant/mailbox policy, not a message property, and is not read"
_NO_VERSIONS = "Graph exposes no version history for messages; Exchange keeps item versions out of the API"

MAIL_EXPORT_DIMENSIONS: Dict[str, Dimension] = {
    "content": (FidelityStatus.DELIVERED, ""),
    "structure": (
        FidelityStatus.DELIVERED,
        "the folder subtree is recorded as each message's folder path, and the sidecar keeps the display chain",
    ),
    "timestamps": (
        FidelityStatus.DELIVERED,
        "the payload file's mtime is stamped from the message, and the sidecar keeps received/sent either way",
    ),
    "item_state": (
        FidelityStatus.DELIVERED,
        "read state, Outlook categories, importance and the draft flag travel in the sidecar",
    ),
    "attachments": (FidelityStatus.DELIVERED, "carried inside each message's MIME, not split into separate files"),
    "permissions": (FidelityStatus.UNSUPPORTED, _NOT_READ_ACLS),
    "versions": (FidelityStatus.UNSUPPORTED, _NO_VERSIONS),
}

MAIL_IMPORT_DIMENSIONS: Dict[str, Dimension] = {
    "content": (FidelityStatus.DELIVERED, ""),
    "structure": (FidelityStatus.DELIVERED, "the folder chain is recreated from each sidecar's display path"),
    "item_state": (
        FidelityStatus.BEST_EFFORT,
        "read state, categories and importance are replayed with one PATCH per message; the follow-up flag is not",
    ),
    "attachments": (FidelityStatus.DELIVERED, "part of the MIME bytes Graph ingests"),
    "timestamps": (
        FidelityStatus.UNSUPPORTED,
        "Exchange stamps an imported message with the import time: receivedDateTime is not settable, so the "
        "original survives only as sentDateTime",
    ),
    "permissions": (FidelityStatus.UNSUPPORTED, _NOT_READ_ACLS),
    "versions": (FidelityStatus.UNSUPPORTED, _NO_VERSIONS),
}

CALENDAR_EXPORT_DIMENSIONS: Dict[str, Dimension] = {
    "content": (FidelityStatus.DELIVERED, ""),
    "structure": (
        FidelityStatus.BEST_EFFORT,
        "a recurring event exports once as its series master; occurrences and cancellations are opt-in, because "
        "exporting a series and its instances both would import the meeting twice",
    ),
    "timestamps": (
        FidelityStatus.DELIVERED,
        "DTSTAMP is the event's own lastModifiedDateTime, so the same event always renders the same bytes",
    ),
    "item_state": (
        FidelityStatus.DELIVERED,
        "show-as, sensitivity, importance, the reminder and Outlook categories ride in the sidecar",
    ),
    "attendees": (FidelityStatus.DELIVERED, "ATTENDEE/ORGANIZER lines are written for another client to read"),
    "attachments": (
        FidelityStatus.UNSUPPORTED,
        "calendar attachments belong to the event and not to the .ics; only hasAttachments is recorded",
    ),
    "permissions": (FidelityStatus.UNSUPPORTED, "calendar sharing is a tenant policy, not an event property"),
    "versions": (FidelityStatus.UNSUPPORTED, "Exchange keeps no per-event version history in Graph"),
}

CALENDAR_IMPORT_DIMENSIONS: Dict[str, Dimension] = {
    "content": (FidelityStatus.DELIVERED, ""),
    "structure": (
        FidelityStatus.DELIVERED,
        "a series is recreated as a seriesMaster carrying Graph's own recurrence object, replayed from the "
        "sidecar rather than parsed back out of RRULE",
    ),
    "item_state": (
        FidelityStatus.DELIVERED,
        "show-as, sensitivity, importance, the reminder and Outlook categories are restored",
    ),
    "attendees": (
        FidelityStatus.BEST_EFFORT,
        "dropped unless CalendarImportOptions(restore_attendees=True): creating an event with attendees makes "
        "Exchange send a real invitation to each of them",
    ),
    "timestamps": (
        FidelityStatus.UNSUPPORTED,
        "Exchange assigns created/modified, the importing user becomes the organizer and iCalUid is service-assigned",
    ),
    "attachments": (
        FidelityStatus.UNSUPPORTED,
        "calendar attachments belong to the event and not to the .ics; only hasAttachments is recorded",
    ),
    "permissions": (FidelityStatus.UNSUPPORTED, "calendar sharing is a tenant policy, not an event property"),
    "versions": (FidelityStatus.UNSUPPORTED, "Exchange keeps no per-event version history in Graph"),
}
