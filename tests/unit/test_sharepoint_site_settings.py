"""Tests for the web-scope site-settings copy (offline)."""

from __future__ import annotations

from office365.migration.sharepoint.resolvers import (
    _apply_web_settings,  # pyright: ignore[reportPrivateUsage]
)
from office365.migration.sharepoint.site_settings import (
    apply_web_settings,
)


class _Web:
    """A web that records the projected GET, the MERGE, and the values written."""

    def __init__(self, title=None, description=None, url="https://contoso.sharepoint.com/sites/t"):
        self._props = {"Url": url, "Title": title, "Description": description}
        self.selected = None
        self.written = {}
        self.updates = 0
        self.fail_update = False

    @property
    def properties(self):
        return self._props

    @property
    def url(self):
        return self._props.get("Url")

    @property
    def server_relative_url(self):
        return self._props.get("ServerRelativeUrl")

    def get_property(self, name):
        return self._props.get(name)

    def select(self, names):
        self.selected = names
        return self

    def set_property(self, name, value):
        self.written[name] = value
        self._props[name] = value
        return self

    def get(self):
        return self

    def update(self):
        if self.fail_update:
            raise RuntimeError("boom")
        self.updates += 1
        return self

    def execute_query(self):
        return self


def test_apply_web_settings_copies_only_differing_values():
    source = _Web(title="Source", description="Same")
    target = _Web(title="Target", description="Same")

    report = apply_web_settings(source, target)

    assert target.written == {"Title": "Source"}
    assert target.updates == 1
    assert report.changed is True
    assert report.applied == {"Title": "Source"}
    assert report.summary() == "site settings: copied Title onto https://contoso.sharepoint.com/sites/t"


def test_a_failing_copy_degrades_to_a_warning():
    source = _Web(title="Source")
    target = _Web(title="Target")
    target.fail_update = True
    warnings: list[str] = []

    report = _apply_web_settings(source, target, True, warnings)

    assert report is None
    assert len(warnings) == 1
    assert warnings[0].startswith("site settings copy failed for https://contoso.sharepoint.com/sites/t")
