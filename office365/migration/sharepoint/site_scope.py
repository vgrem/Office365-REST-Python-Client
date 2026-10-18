"""Report the site-level scope a client-side migration does not recreate.

A migration replays a list's columns, content types and views, copies the web's
``Title``/``Description`` and its branding, and says nothing about two things that
decide what the target site can actually *do*:

* **activated features** — on the web and on its site collection. A site without
  the publishing, records-management or document-id feature is not the same site,
  even when every list and file arrived.
* **regional settings** — time zone, locale, work days, calendar. Values that
  render and filter by date depend on them.

Both are readable over REST, so they are compared instead of assumed, and a
difference is reported rather than repaired:

* Activating a feature has side effects the source did not ask for at this point in
  the run (a publishing feature installs page layouts and swaps the master page),
  and deactivating one is not something a re-run undoes. It stays an explicit,
  out-of-band decision.
* Regional settings have no working REST write path (setting ``TimeZone`` id does
  not change the web's zone), which is why
  :mod:`office365.migration.sharepoint.site_settings` never attempts them.

The comparison is **by presence and by value**, read-only: two GETs per side for
the features, one for the regional settings and one for the time zone. Only what
the *source* has and the target lacks is a finding — a target feature the source
does not have is carried in the result (it is a real difference an operator may
want to see) but is not a fidelity loss, so it does not make the report fail.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.features.feature import Feature
    from office365.sharepoint.webs.web import Web

logger = logging.getLogger(__name__)

__all__ = [
    "SiteScope",
    "SiteScopeDiff",
    "capture_site_scope",
    "compare_site_scope",
    "site_scope_note",
]

#: How many feature/regional names a single note spells out before counting the rest.
_MAX_NAMES_IN_NOTE = 5

#: Regional properties that change how values render or filter. A property the
#: server does not return is ``None`` on both sides, which compares equal.
_REGIONAL_PROPERTIES = (
    "LocaleId",
    "WorkDays",
    "FirstDayOfWeek",
    "FirstWeekOfYear",
    "CalendarType",
    "AdjustHijriDays",
    "DateSeparator",
    "TimeSeparator",
    "Time24",
    "DateFormat",
)


def _normalized(feature_id: Optional[str]) -> str:
    """A feature id as a comparable key (lowercase, no braces)."""
    return str(feature_id or "").strip().strip("{}").lower()


def _feature_ids(features: Iterable["Feature"]) -> List[str]:
    """The activated feature ids of a collection, sorted and de-duplicated."""
    ids = {_normalized(feature.definition_id) for feature in features}
    ids.discard("")
    return sorted(ids)


def _read_features(collection: Any) -> List[str]:
    """The ids of one activated-feature collection (web or site collection)."""
    return _feature_ids(collection.get().execute_query())


def _read_regional(web: "Web") -> Dict[str, Any]:
    """The comparable regional settings of ``web``, plus the time zone's identity."""
    settings = web.regional_settings.get().execute_query()
    values: Dict[str, Any] = {name: settings.properties.get(name) for name in _REGIONAL_PROPERTIES}
    values["TimeZoneId"], values["TimeZone"] = _read_time_zone(settings)
    return values


def _read_time_zone(settings: Any) -> Tuple[Optional[int], Optional[str]]:
    """``(id, description)`` of the web's time zone, or ``(None, None)`` if unreadable."""
    try:
        zone = settings.time_zone.get().execute_query()
    except Exception as e:  # noqa: BLE001 — a time zone that cannot be read is not a finding
        logger.debug("read time zone failed: %s", e)
        return None, None
    return zone.properties.get("Id"), zone.properties.get("Description")


@dataclass
class SiteScope:
    """One site's site-level scope, as captured (the comparable projection)."""

    web_features: List[str] = field(default_factory=list)
    site_features: List[str] = field(default_factory=list)
    regional: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-serializable form."""
        return {
            "web_features": list(self.web_features),
            "site_features": list(self.site_features),
            "regional": dict(self.regional),
        }


@dataclass
class SiteScopeDiff:
    """What the source has and the target does not, plus the settings that differ."""

    missing_web_features: List[str] = field(default_factory=list)
    missing_site_features: List[str] = field(default_factory=list)
    extra_web_features: List[str] = field(default_factory=list)
    extra_site_features: List[str] = field(default_factory=list)
    regional: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        """Whether the target carries everything the source had (extras are not a loss)."""
        return not self.missing_web_features and not self.missing_site_features and not self.regional

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-serializable form (``regional`` maps a name to ``[source, target]``)."""
        return {
            "missing_web_features": list(self.missing_web_features),
            "missing_site_features": list(self.missing_site_features),
            "extra_web_features": list(self.extra_web_features),
            "extra_site_features": list(self.extra_site_features),
            "regional": {name: [value, other] for name, (value, other) in self.regional.items()},
        }


def capture_site_scope(context: "ClientContext") -> SiteScope:
    """Read one site's activated features and comparable regional settings.

    Args:
        context: The site's context. The web-scope features come from
            ``context.web``, the site-collection ones from ``context.site``.
    """
    return SiteScope(
        web_features=_read_features(context.web.features),
        site_features=_read_features(context.site.features),
        regional=_read_regional(context.web),
    )


def compare_site_scope(source_context: "ClientContext", target_context: "ClientContext") -> SiteScopeDiff:
    """What ``target_context``'s site lacks that ``source_context``'s has (read-only).

    Args:
        source_context: The site the migration reads from.
        target_context: The site the migration wrote to.
    """
    source = capture_site_scope(source_context)
    target = capture_site_scope(target_context)
    return SiteScopeDiff(
        missing_web_features=[name for name in source.web_features if name not in set(target.web_features)],
        missing_site_features=[name for name in source.site_features if name not in set(target.site_features)],
        extra_web_features=[name for name in target.web_features if name not in set(source.web_features)],
        extra_site_features=[name for name in target.site_features if name not in set(source.site_features)],
        regional={
            name: (value, target.regional.get(name))
            for name, value in source.regional.items()
            if target.regional.get(name) != value
        },
    )


def _sample_names(names: List[str]) -> str:
    """Name a few entries inline, counting the rest."""
    shown = ", ".join(names[:_MAX_NAMES_IN_NOTE])
    if len(names) <= _MAX_NAMES_IN_NOTE:
        return shown
    return f"{shown} (+{len(names) - _MAX_NAMES_IN_NOTE} more)"


def _regional_note(regional: Dict[str, Tuple[Any, Any]]) -> str:
    """One clause naming each differing regional setting: ``TimeZone: 'a' vs 'b'``."""
    return "; ".join(f"{name}: {value!r} vs {other!r}" for name, (value, other) in regional.items())


def site_scope_note(diff: SiteScopeDiff, source_url: Optional[str] = None) -> Optional[str]:
    """A warning line for the site-level gap, or ``None`` when there is none.

    Args:
        diff: The result of :func:`compare_site_scope`.
        source_url: The *source* site's URL, so the note says which site is short.
    """
    if diff.is_empty:
        return None
    parts: List[str] = []
    if diff.missing_web_features:
        parts.append(f"{len(diff.missing_web_features)} web feature(s): {_sample_names(diff.missing_web_features)}")
    if diff.missing_site_features:
        parts.append(
            f"{len(diff.missing_site_features)} site-collection feature(s): {_sample_names(diff.missing_site_features)}"
        )
    if diff.regional:
        parts.append(f"regional settings differ ({_regional_note(diff.regional)})")
    return (
        f"site scope is not replayed: the target of {source_url or 'this web'} lacks "
        + "; ".join(parts)
        + " — activating a feature changes what the site can do and is not undone by re-running the "
        "migration, and regional settings have no working REST write path, so both are reported; "
        "activate the missing features out of band (Enable-SPFeature) if the site depends on them"
    )
