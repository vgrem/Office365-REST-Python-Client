"""Copy the web-scope site settings a client-side migration can carry.

Replaying a list's structure reproduces its columns, content types and views —
never the web that hosts them, so a migrated site would otherwise keep the
*target* web's identity. Two of those settings are plain writable strings over
REST and are what a user actually sees (site header, search results, the site
card), so they are copied rather than left silently source-specific:

* ``Title``
* ``Description``

Only **differing** values are written: a blind MERGE of an already-matching
setting is not harmless (it bumps the web's metadata and, for some properties,
re-triggers server-side side effects), and it would make every re-run look like a
change. The copy is therefore idempotent by construction.

What this module deliberately does *not* carry is named instead of being implied
away (in the docs, and in the ``site_settings`` fidelity dimension's note):

* **branding** — master page, theme, `SiteLogoUrl`, alternate CSS. Those are
  carried by :mod:`office365.migration.sharepoint.branding` instead, whose rules
  are different enough (path rebasing, assets that may not exist on the target) to
  keep it a separate concern.
* **site-collection and regional settings** — time zone, locale, quotas,
  sharing capability, hub association. REST exposes no working write path for
  them (setting a `TimeZone` id does not change the web's zone), so they are not
  attempted.

The mode vocabulary is the SPMT-flavoured string on
:attr:`~office365.migration.settings.MigrationSettings.migrate_site_settings`:
``PRESERVE_ALL_SETTINGS`` (copy the settings above) or ``NONE`` (leave the target
web alone). An unrecognized value raises rather than silently doing nothing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from office365.sharepoint.webs.web import Web

logger = logging.getLogger(__name__)

__all__ = [
    "SITE_SETTINGS_PRESERVE",
    "SITE_SETTINGS_SKIP",
    "WebSettings",
    "WebSettingsReport",
    "apply_web_settings",
    "parse_site_settings_mode",
    "verify_web_settings",
]

#: Copy the web settings this module carries (the ``migrate_site_settings`` default).
SITE_SETTINGS_PRESERVE = "PRESERVE_ALL_SETTINGS"
#: Leave the target web's own settings untouched.
SITE_SETTINGS_SKIP = "NONE"

_MODES: Dict[str, bool] = {SITE_SETTINGS_PRESERVE: True, SITE_SETTINGS_SKIP: False}

#: The web properties a copy carries. Both are plain strings on ``SP.Web``.
_CARRIED = ("Title", "Description")


def parse_site_settings_mode(mode: Optional[str]) -> bool:
    """Whether ``mode`` asks for the site settings to be copied.

    Args:
        mode: The ``migrate_site_settings`` value (``None`` means "not set", which
            preserves, matching the settings default).

    Returns:
        ``True`` to copy the carried settings, ``False`` to leave the target alone.

    Raises:
        ValueError: If the value is not one of the supported modes — a typo must
            not silently disable (or enable) the copy.
    """
    if mode is None:
        return True
    key = str(mode).strip().upper()
    if key not in _MODES:
        raise ValueError(f"unknown migrate_site_settings {mode!r}; expected one of {sorted(_MODES)}")
    return _MODES[key]


@dataclass(frozen=True)
class WebSettings:
    """The web-scope settings a copy carries, read from one projected GET."""

    title: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def capture(cls, web: "Web") -> "WebSettings":
        """Read a web's carried settings (one GET projecting ``Title``/``Description``)."""
        properties = web.select(list(_CARRIED)).get().execute_query().properties
        return cls(title=properties.get("Title"), description=properties.get("Description"))

    def values(self) -> List[tuple[str, Optional[str]]]:
        """The carried settings as ``(REST property name, value)`` pairs."""
        return [("Title", self.title), ("Description", self.description)]

    def changed(self, target: "WebSettings") -> Dict[str, str]:
        """The properties whose value differs from ``target`` (never blank differences).

        A web always reports a ``Title``, so an unset value is written as an empty
        string rather than as ``null`` — the server rejects a null for these.
        """
        current = {"Title": target.title, "Description": target.description}
        changes: Dict[str, str] = {}
        for name, value in self.values():
            if (value or "") == (current[name] or ""):
                continue
            changes[name] = value if value is not None else ""
        return changes


@dataclass
class WebSettingsReport:
    """What a web-settings copy wrote — empty ``applied`` when nothing differed."""

    url: str
    applied: Dict[str, str] = field(default_factory=dict)

    @property
    def changed(self) -> bool:
        """Whether the copy wrote anything at all."""
        return bool(self.applied)

    def summary(self) -> str:
        """A one-line note for the session's warnings (empty when nothing was written)."""
        if not self.applied:
            return ""
        names = ", ".join(sorted(self.applied))
        return f"site settings: copied {names} onto {self.url}"


def _web_url(web: "Web") -> str:
    """A web's absolute URL, falling back to the site URL of its context.

    A projected read (``select(["Title", "Description"]).get()``) replaces the
    loaded properties with the ones it asked for, so ``Url`` may be gone by the
    time a note needs it — the context still knows which site the web belongs to.
    """
    for name in ("Url", "ServerRelativeUrl"):
        value = web.get_property(name)
        if value:
            return str(value)
    return str(getattr(getattr(web, "context", None), "base_url", "") or "")


def apply_web_settings(source_web: "Web", target_web: "Web", *, preserve: bool = True) -> WebSettingsReport:
    """Copy the carried web settings from ``source_web`` onto ``target_web``.

    Reads both sides (one projected GET each), writes only the properties that
    differ (one MERGE on the target web), so a re-run is a no-op.

    Args:
        source_web: The source web to read the settings from.
        target_web: The target web to write them to.
        preserve: ``False`` leaves the target web untouched.
    """
    url = _web_url(target_web)
    if not preserve:
        return WebSettingsReport(url=url)
    changes = WebSettings.capture(source_web).changed(WebSettings.capture(target_web))
    if not changes:
        return WebSettingsReport(url=url)
    for name, value in changes.items():
        target_web.set_property(name, value)
    target_web.update().execute_query()
    report = WebSettingsReport(url=url, applied=dict(changes))
    logger.info(report.summary())
    return report


def verify_web_settings(source_web: "Web", target_web: "Web") -> List[str]:
    """Reconcile the carried web settings (read-only; one finding per property).

    Args:
        source_web: The source web that was copied.
        target_web: The target web to check.
    """
    source = WebSettings.capture(source_web)
    target = WebSettings.capture(target_web)
    url = _web_url(target_web)
    notes: List[str] = []
    for name, value in source.values():
        current = dict(target.values())[name]
        if (value or "") == (current or ""):
            continue
        notes.append(f"site settings: {url} {name} is {current!r}, source has {value!r}")
    return notes
