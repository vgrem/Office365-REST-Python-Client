"""Carry a web's look-and-feel settings onto the target web.

Replaying a list's structure and copying its content leaves the *web* looking like
the target: its own master page, its own theme, no logo. Four of the branding
properties are plain writable strings over REST and a MERGE of them is accepted
(live-verified on SharePoint Online) — ``SiteLogoUrl``, ``AlternateCssUrl``,
``MasterUrl``/``CustomMasterUrl`` and ``ThemedCssFolderUrl`` — so they are carried
rather than handed off. Three things make a blind copy wrong:

* every value is a **path inside the source site**, so the source's
  ``/sites/team_in`` prefix is rebased onto the target's; copying it verbatim
  would leave the migrated web pointing back at the site it came from;
* every one of them names an **asset** — a master page or theme folder in a gallery
  this migration never copies (``_catalogs/masterpage``, ``_catalogs/theme`` are
  hidden lists), a logo, an alternate CSS — so a value is written only when the
  target actually has the file or folder. Otherwise the web keeps its own and the
  gap is reported, because a blank or dangling master page would break every page
  on the site and a logo can point at a service endpoint
  (``_api/GroupService/GetGroupImage``) that has no counterpart to copy;
* only the logo and the alternate CSS can be **cleared**: writing a blank
  ``MasterUrl`` would leave the web without a master page at all.

Only differing values are written, so a re-run is a no-op.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Dict, List, Optional
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from office365.sharepoint.webs.web import Web

logger = logging.getLogger(__name__)

__all__ = [
    "WebBranding",
    "WebBrandingReport",
    "apply_web_branding",
    "verify_web_branding",
]

_LOGO = "SiteLogoUrl"
_CSS = "AlternateCssUrl"
_MASTER = "MasterUrl"
_CUSTOM_MASTER = "CustomMasterUrl"
_THEME = "ThemedCssFolderUrl"

#: The properties a copy carries, plus the web's own path (needed to rebase them).
_CAPTURED = ("ServerRelativeUrl", _LOGO, _CSS, _MASTER, _CUSTOM_MASTER, _THEME)

#: Branding properties that name an asset on the target, and what kind of asset.
#: A value is copied only where the target resolves it, so a source-site pointer is
#: reported instead of written as a dangling one.
_ASSETS: Dict[str, str] = {
    _LOGO: "file",
    _CSS: "file",
    _MASTER: "file",
    _CUSTOM_MASTER: "file",
    _THEME: "folder",
}

#: Branding properties a copy may clear when the source has none.
_CLEARABLE = frozenset({_LOGO, _CSS})


def _web_url(web: "Web") -> str:
    """A web's absolute URL, falling back to the site URL of its context.

    A projected read replaces the loaded properties with the ones it asked for, so
    ``Url`` may be gone by the time a note needs it.
    """
    for name in ("Url", "ServerRelativeUrl"):
        value = web.get_property(name)
        if value:
            return str(value)
    return str(getattr(getattr(web, "context", None), "base_url", "") or "")


def _rebase(value: Optional[str], source_path: Optional[str], target_path: Optional[str]) -> Optional[str]:
    """Point a server-relative branding value at the target site instead of the source.

    A value is usually site-relative (``/sites/team_in/_catalogs/masterpage/x.master``)
    but can be an absolute URL carrying the same path, so the path is replaced
    wherever it appears rather than only at the start.
    """
    if not value or not source_path or not target_path or source_path == target_path:
        return value
    if value == source_path:
        return target_path
    return value.replace(source_path + "/", target_path + "/", 1)


@dataclass(frozen=True)
class WebBranding:
    """The branding properties a copy carries, read from one projected GET."""

    web_path: Optional[str] = None
    site_logo_url: Optional[str] = None
    alternate_css_url: Optional[str] = None
    master_url: Optional[str] = None
    custom_master_url: Optional[str] = None
    themed_css_folder_url: Optional[str] = None

    @classmethod
    def capture(cls, web: "Web") -> "WebBranding":
        """Read a web's branding (one GET projecting the carried properties)."""
        properties = web.select(list(_CAPTURED)).get().execute_query().properties
        return cls(
            web_path=properties.get("ServerRelativeUrl"),
            site_logo_url=properties.get(_LOGO),
            alternate_css_url=properties.get(_CSS),
            master_url=properties.get(_MASTER),
            custom_master_url=properties.get(_CUSTOM_MASTER),
            themed_css_folder_url=properties.get(_THEME),
        )

    def values(self) -> List[tuple[str, Optional[str]]]:
        """The carried branding as ``(REST property name, value)`` pairs."""
        return [
            (_LOGO, self.site_logo_url),
            (_CSS, self.alternate_css_url),
            (_MASTER, self.master_url),
            (_CUSTOM_MASTER, self.custom_master_url),
            (_THEME, self.themed_css_folder_url),
        ]

    def rebased(self, source_path: Optional[str], target_path: Optional[str]) -> "WebBranding":
        """The same branding with every path moved from the source site to the target's."""
        if not source_path or not target_path or source_path == target_path:
            return self
        return replace(
            self,
            web_path=target_path,
            site_logo_url=_rebase(self.site_logo_url, source_path, target_path),
            alternate_css_url=_rebase(self.alternate_css_url, source_path, target_path),
            master_url=_rebase(self.master_url, source_path, target_path),
            custom_master_url=_rebase(self.custom_master_url, source_path, target_path),
            themed_css_folder_url=_rebase(self.themed_css_folder_url, source_path, target_path),
        )


@dataclass
class WebBrandingReport:
    """What a branding copy wrote, and which properties it left to the target."""

    url: str
    applied: Dict[str, str] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)

    @property
    def changed(self) -> bool:
        """Whether the copy wrote anything at all."""
        return bool(self.applied)

    def summary(self) -> str:
        """A one-line note per outcome (empty when the target already matched)."""
        notes: List[str] = []
        if self.applied:
            notes.append(f"branding: copied {', '.join(sorted(self.applied))} onto {self.url}")
        for name, reason in sorted(self.skipped.items()):
            notes.append(f"branding: {self.url} keeps its own {name} — {reason}")
        return "; ".join(notes)


def _asset_path(value: str) -> str:
    """The server-relative path a branding value points at.

    A branding value may be server-relative (``/sites/team_out/SiteAssets/logo.png``)
    or absolute; the asset lookup only speaks the former, so an absolute URL is
    reduced to its path.
    """
    if "://" in value:
        return urlsplit(value).path or value
    return value


def _exists_on_target(web: "Web", path: str, kind: str) -> bool:
    """Whether ``path`` names a file/folder the target web actually has."""
    path = _asset_path(path)
    try:
        if kind == "folder":
            web.get_folder_by_server_relative_path(path).get().execute_query()
        else:
            web.get_file_by_server_relative_url(path).get().execute_query()
    except Exception:  # noqa: BLE001 — an unreadable path is treated as "not on the target"
        return False
    return True


def apply_web_branding(source_web: "Web", target_web: "Web", *, preserve: bool = True) -> WebBrandingReport:
    """Copy a web's branding onto the target, skipping what the target has no asset for.

    Reads both sides (one projected GET each), rebases the source's paths onto the
    target site, and writes only the properties that differ (one MERGE on the
    target web), so a re-run is a no-op. A value naming an asset the target does not
    have is reported instead of written.

    Args:
        source_web: The source web to read the branding from.
        target_web: The target web to write it to.
        preserve: ``False`` leaves the target web untouched.
    """
    url = _web_url(target_web)
    if not preserve:
        return WebBrandingReport(url=url)
    source = WebBranding.capture(source_web)
    target = WebBranding.capture(target_web)
    wanted = source.rebased(source.web_path, target.web_path)
    current = dict(target.values())
    applied: Dict[str, str] = {}
    skipped: Dict[str, str] = {}
    for name, value in wanted.values():
        if (value or "") == (current[name] or ""):
            continue
        if not value:
            if name in _CLEARABLE:
                applied[name] = ""
            else:
                skipped[name] = "the source has none"
            continue
        kind = _ASSETS.get(name)
        if kind is not None and not _exists_on_target(target_web, value, kind):
            skipped[name] = f"the target has no {value}"
            continue
        applied[name] = value
    if applied:
        for name, value in applied.items():
            target_web.set_property(name, value)
        target_web.update().execute_query()
    report = WebBrandingReport(url=url, applied=applied, skipped=skipped)
    note = report.summary()
    if note:
        logger.info(note)
    return report


def verify_web_branding(source_web: "Web", target_web: "Web") -> List[str]:
    """Reconcile a web's branding (read-only; one finding per property).

    The source's paths are rebased before comparing, so a migrated master page is
    not reported merely because it now lives under the target site's path.

    Args:
        source_web: The source web that was copied.
        target_web: The target web to check.
    """
    source = WebBranding.capture(source_web)
    target = WebBranding.capture(target_web)
    wanted = source.rebased(source.web_path, target.web_path)
    current = dict(target.values())
    url = _web_url(target_web)
    notes: List[str] = []
    for name, value in wanted.values():
        if (value or "") == (current[name] or ""):
            continue
        notes.append(f"branding: {url} {name} is {current[name]!r}, source has {value!r}")
    return notes
