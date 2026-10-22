"""Calendar records — one event's sidecar, and the artefacts a migration builds from it.

An exported event is two files: an ``.ics`` (the portable artefact — Outlook, Google
Calendar and Thunderbird all open it) and a JSON sidecar carrying what iCalendar cannot
express faithfully (Graph ids, the recurrence object Graph normalises, the online-meeting
provider, sensitivity/importance). The sidecar is the import contract; the ``.ics`` is
regenerated from it, so an export is reproducible: the same event always produces the
same bytes.

The sidecar **is the event as the model serializes it** — ``event.to_json()`` plus the
three things no model can know (the calendar it came from, the path it is written to,
and that calendar's display path). So nothing here lists a field: a column the model
declares is exported, replayed and verified with no function edited, and the keys are
Graph's own spellings (``isAllDay``, ``showAs``, ``iCalUId``) because that is what the
model answers and what an import posts back.

Spelling lives in two tables, not here: which iCalendar token a Graph value becomes is
:mod:`office365.migration.outlook.calendar_profile`, and the document itself is written
by :mod:`office365.migration.outlook.calendar_codec`.

Unlike mail, this file is *built* rather than fetched, so a byte checksum is a valid
verification of an export: there is no server re-serialization in the middle. An
*import* is the other way round — Exchange re-serializes what it accepts and assigns the
meeting metadata — so it is verified by a digest of the event's restorable fields
(:func:`event_digest`).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Mapping, cast

from office365.migration.outlook.calendar_codec import MAX_LINE_OCTETS, encode
from office365.migration.outlook.calendar_profile import COMPARED, wall_clock
from office365.migration.outlook.models import mail_slug
from office365.outlook.calendar.events.event import Event
from office365.runtime.converters.value import serialize_value
from office365.runtime.odata.v4.json_format import V4JsonFormat

#: Graph event properties an export reads: every column the model declares.
#: Derived rather than listed, so a $select cannot disagree with the getters that
#: consume it — the class of bug that produced ``iCalUid`` (one capital short of
#: the real ``iCalUId``, silently ``None``) is now unrepresentable. Navigation
#: properties are excluded by construction: ``$select`` rejects them.
EVENT_COLUMNS = Event.select_all()

#: Event types that stand on their own. An ``occurrence``/``exception`` belongs to
#: its ``seriesMaster`` (exported once, as a series), so exporting the instances
#: too would duplicate every recurring meeting — the default skips them.
STANDALONE_EVENT_TYPES = ("singleInstance", "seriesMaster")

#: The keys an envelope holds that no model does: where the event came from, where its
#: document is written, and the same for a reader who should not have to parse a path.
PROVENANCE = ("calendar_path", "calendar_display_path", "ics_path")
assert not set(PROVENANCE) & frozenset(EVENT_COLUMNS), "a provenance key collides with a column the model declares"

#: Keys a sidecar written before the envelope became the model's own JSON carries. Their
#: presence means the tree was exported by a version that spelled its own vocabulary
#: (``graph_id``/``is_all_day``), and reading it as Graph's would silently find nothing.
LEGACY_KEYS = ("graph_id", "is_all_day", "show_as", "ical_uid")


@dataclass
class CalendarExportOptions:
    """What a calendar export includes."""

    #: Name of the top folder in the export tree (``None`` uses the calendar's own
    #: display name, slugified). Set it to keep a stable root across renames.
    root_name: str | None = None
    #: Export the individual occurrences/exceptions of a recurring event as well as
    #: the series. Off by default: a series already carries its pattern, and each
    #: instance copied as a standalone event would show up twice in the target.
    include_recurring_instances: bool = False
    #: Export cancelled events. Off by default: a cancelled event is a tombstone,
    #: and the import creates live events, so replaying one would resurrect a
    #: meeting the user cancelled.
    include_cancelled: bool = False
    #: Extra Graph event properties to record in the sidecar (camelCase names).
    extra_properties: list[str] = field(default_factory=list)


@dataclass
class CalendarImportOptions:
    """What an import of an exported calendar restores.

    Pass the *same* options object to both adapters of an import job: the source
    computes the content digest of what the target promises to restore, so the two
    sides have to agree on the fields to be comparable (see :func:`event_digest`).
    """

    #: Re-add the attendee list. **Off by default**, because creating an event with
    #: attendees makes Exchange send an invitation to every one of them (measured:
    #: a copy lands in the organizer's Sent Items, and ``responseRequested: false``
    #: does not suppress it) — so a historical import would spam colleagues with
    #: meetings they already had. With it off the attendees stay in the sidecar and
    #: the run reports how many were dropped.
    restore_attendees: bool = False
    #: Re-apply the category labels.
    restore_categories: bool = True
    #: Give every created event a deterministic ``transactionId``, so two concurrent
    #: runs of the same import collide on the server rather than both writing.
    use_transaction_ids: bool = True


def event_key(envelope: Mapping[str, Any]) -> str:
    """The identity an export is keyed by: the Graph event id.

    Deliberately not ``iCalUId``: Exchange assigns one to a *meeting* but not to a
    plain appointment (measured — an event created through the API comes back with
    ``iCalUId: null`` even on a later read), so keying on it would let a re-run see
    the same event under a new identity and write a second copy. The Graph id is
    stable for the event's life in its calendar. ``iCalUId`` is still what other
    calendar clients match on, so it rides in the sidecar and becomes the ``.ics``
    ``UID`` when present.
    """
    return str(envelope.get("id") or envelope.get("iCalUId") or "")


def event_kind(event) -> str | None:
    """The wire name of an event's ``type``: ``singleInstance``, ``seriesMaster``, …

    The getter answers with the generated enum, whose members carry the CSDL ordinals
    (``EventType.singleInstance.value == "0"``) rather than what the service speaks;
    ``serialize_value`` is the library's answer to that — the member *name*.
    """
    return serialize_value(event.type_)


def _dest_path(stamp: datetime | None, subject: Any, key: str, calendar_path: str) -> str:
    """``<calendar>/<date>_<slug>_<id digest>.ics``, from the three things that decide it.

    Deterministic for a given event, so a re-run finds the file it wrote. The date is
    the event's start date — a calendar sorted by filename reads chronologically — and
    the digest of the key keeps same-titled events on the same day apart.
    """
    date = stamp.strftime("%Y-%m-%d") if stamp else ""
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
    stem = "_".join(part for part in (date, mail_slug(subject), digest) if part)
    name = f"{stem}.ics"
    return f"{calendar_path}/{name}" if calendar_path else name


def event_dest_path(event, calendar_path: str) -> str:
    """The export path for a loaded event — see :func:`_dest_path` for the shape."""
    started = event.start.as_datetime() if event.start else None
    return _dest_path(started, event.subject, str(event.id or event.ical_uid or ""), calendar_path)


def event_envelope(
    event,
    calendar_path: str = "",
    extra_properties: list[str] | None = None,
    display_path: str | None = None,
) -> dict[str, Any]:
    """The sidecar for an event read from the service: the model's own JSON, plus provenance.

    ``to_json()`` is the library's serializer, so the sidecar keeps Graph's shape
    (``start``/``end`` as a wall clock and zone name, ``recurrence`` as Graph's object)
    rather than a second spelling this package would have to keep in step — and an
    import posts it back verbatim, which is what makes the round trip exact.
    """
    envelope = event.to_json()
    envelope["calendar_path"] = calendar_path
    envelope["calendar_display_path"] = display_path or calendar_path
    envelope["ics_path"] = event_dest_path(event, calendar_path)
    for name in extra_properties or []:
        envelope[name] = serialize_value(event.get_property(name))
    return envelope


def _model_spelling(envelope: Mapping[str, Any]) -> None:
    """Refuse a sidecar written before the envelope was the model's own JSON."""
    if any(name in envelope for name in LEGACY_KEYS):
        raise ValueError(
            "this sidecar spells its own keys (``graph_id``, ``is_all_day``) and was written by an older"
            " exporter: re-export the calendar and import that tree"
        )


def event_ics(envelope: Mapping[str, Any]) -> bytes:
    """The event as an ``.ics`` document (see the codec's :func:`encode`)."""
    _model_spelling(envelope)
    return encode(envelope)


def event_create_payload(envelope: Mapping[str, Any], options: CalendarImportOptions | None = None) -> dict[str, Any]:
    """The Graph ``POST /events`` body for an envelope.

    The model reads its own sidecar and spells the body: ``hydrate`` fills an ``Event``
    from the envelope (coercing each value to its declared type), and ``to_json`` with a
    profile emits it as a request payload, dropping what the service owns
    (``@odata(readonly=True)``: the id, the organizer, the attendee responses, the audit
    stamps) and the ``extra_properties`` an export records only to survive a round trip.
    What is left is exactly what an import may restore; the options then decide how much
    of it to send. Nothing here spells a Graph field.
    """
    options = options or CalendarImportOptions()
    _model_spelling(envelope)

    # A draft has no context: nothing is queried through it, it is only spelled back out.
    draft = Event(None)  # type: ignore[arg-type]
    V4JsonFormat().hydrate(draft, envelope, persist_changes=True)
    spelled = cast(Dict[str, Any], draft.to_json(V4JsonFormat("none")))
    body: dict[str, Any] = {
        name: value
        for name, value in spelled.items()
        # The model's own vocabulary, and only what it can actually say: an undeclared key
        # is provenance an export records for its ledger, and a null/empty value is the
        # absence of a statement, not a request to clear a field.
        if name in Event._odata_meta and value not in (None, {}, [])
    }
    start, end = body.get("start") or {}, body.get("end") or {}
    if not start.get("dateTime") or not end.get("dateTime"):
        raise ValueError("the sidecar has no start/end dateTime: an event cannot be created without a time range")
    if isinstance(body.get("recurrence"), str):
        raise ValueError(
            f"the sidecar records the recurrence as text ({body['recurrence'][:60]!r}): it was written by a version"
            " of the exporter that serialised Graph's typed object with ``repr``, so the series cannot be"
            " replayed — re-export the calendar and import that tree"
        )

    content = body.get("body")
    if not (content and content.get("content")):
        body.pop("body", None)
    else:
        # Graph is case-insensitive here (measured); ``HTML``/``Text`` is what an import has
        # always sent, so the model's ``html`` is re-cased rather than the wire moving silently.
        content["contentType"] = "HTML" if str(content.get("contentType")).lower() == "html" else "Text"
    if not options.restore_attendees:
        body.pop("attendees", None)
    else:
        # ``status`` is the attendee's own reply, which Exchange assigns: an import sends the
        # people, not the answers. Dropped here until a live create probe says otherwise.
        for attendee in body["attendees"]:
            attendee.pop("status", None)
    if not options.restore_categories:
        body.pop("categories", None)
    if options.use_transaction_ids:
        body["transactionId"] = event_transaction_id(envelope)
    return body


def event_canonical(envelope: Mapping[str, Any], options: CalendarImportOptions | None = None) -> dict[str, Any]:
    """The restored fields in comparable form, one profile row per field.

    A field the import declines to restore (``restore_attendees``,
    ``restore_categories``) leaves the canonical form, which is why the source and the
    target of one job must share the options object.
    """
    options = options or CalendarImportOptions()
    return {rule.key: rule.normalise(envelope) for rule in COMPARED if not rule.gate or getattr(options, rule.gate)}


def event_digest(envelope: Mapping[str, Any], options: CalendarImportOptions | None = None) -> str:
    """A digest of the fields an import restores, for verifying that it did.

    Not the ``.ics`` bytes: the other side of an import is Exchange, which re-serializes
    the body and assigns the meeting metadata, so the comparable artefact is the *event*.
    Which fields take part — and what each is normalised to — is
    :data:`calendar_profile.COMPARED`, so a field the sidecar gains is a row there rather
    than a line in this function.
    """
    _model_spelling(envelope)
    canonical = json.dumps(event_canonical(envelope, options), sort_keys=True, default=str)
    return hashlib.md5(canonical.encode("utf-8")).hexdigest()


def event_dropped_attendees(envelope: Mapping[str, Any], options: CalendarImportOptions | None = None) -> int:
    """How many attendee entries the import leaves out, and so does not invite.

    Creating an event with attendees makes Exchange mail every one of them (measured),
    which is why replaying the list is opt-in; the count is what the run reports so the
    omission is a number rather than a silence.
    """
    options = options or CalendarImportOptions()
    if options.restore_attendees:
        return 0
    return sum(1 for item in envelope.get("attendees") or [] if (item.get("emailAddress") or {}).get("address"))


def event_dedup_key(envelope: Mapping[str, Any]) -> tuple[str, str | None, str | None]:
    """The key a target matches an existing event on: subject and start.

    A created event comes back with ``iCalUId: null`` and a fresh Graph id, so neither
    of the source's identities survives the import — subject plus wall clock (and the
    zone it is in) is what is left to recognise a re-run's own work by.
    """
    wall, zone = wall_clock(envelope.get("start"))
    return (str(envelope.get("subject") or ""), wall, zone)


def event_transaction_id(envelope: Mapping[str, Any]) -> str:
    """A deterministic ``transactionId`` for an exported event."""
    key = event_key(envelope) or str(envelope.get("ics_path") or "")
    return "mig-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:32]


__all__ = [
    "EVENT_COLUMNS",
    "LEGACY_KEYS",
    "MAX_LINE_OCTETS",
    "PROVENANCE",
    "STANDALONE_EVENT_TYPES",
    "CalendarExportOptions",
    "CalendarImportOptions",
    "event_canonical",
    "event_create_payload",
    "event_dedup_key",
    "event_dest_path",
    "event_digest",
    "event_dropped_attendees",
    "event_envelope",
    "event_ics",
    "event_key",
    "event_kind",
    "event_transaction_id",
]
