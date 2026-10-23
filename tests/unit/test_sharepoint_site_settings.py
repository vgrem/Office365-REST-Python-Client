"""Tests for the web-scope site-settings copy (offline)."""

from __future__ import annotations

from office365.migration.sharepoint.resolvers import (
    _apply_web_settings,  # pyright: ignore[reportPrivateUsage]
)
from office365.migration.sharepoint.site_settings import (
    SITE_SETTINGS_PRESERVE,
    SITE_SETTINGS_SKIP,
    WebSettings,
    WebSettingsReport,
    apply_web_settings,
    parse_site_settings_mode,
    verify_web_settings,
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


def test_site_settings_mode_maps_both_spelling_variants():
    assert parse_site_settings_mode(None) is True
    assert parse_site_settings_mode(SITE_SETTINGS_PRESERVE) is True
    assert parse_site_settings_mode("preserve_all_settings") is True
    assert parse_site_settings_mode(SITE_SETTINGS_SKIP) is False
    assert parse_site_settings_mode(" none ") is False


def test_capture_projects_the_carried_properties():
    web = _Web(title="Source", description="The source site")

    settings = WebSettings.capture(web)

    assert web.selected == ["Title", "Description"]
    assert settings == WebSettings(title="Source", description="The source site")
    assert settings.values() == [("Title", "Source"), ("Description", "The source site")]


def test_apply_web_settings_copies_only_differing_values():
    source = _Web(title="Source", description="Same")
    target = _Web(title="Target", description="Same")

    report = apply_web_settings(source, target)

    assert target.written == {"Title": "Source"}
    assert target.updates == 1
    assert report.changed is True
    assert report.applied == {"Title": "Source"}
    assert report.summary() == "site settings: copied Title onto https://contoso.sharepoint.com/sites/t"


def test_apply_web_settings_is_a_no_op_when_nothing_differs():
    source = _Web(title="Same", description="Same")
    target = _Web(title="Same", description="Same")

    report = apply_web_settings(source, target)

    assert target.written == {}
    assert target.updates == 0
    assert report == WebSettingsReport(url="https://contoso.sharepoint.com/sites/t")
    assert report.changed is False
    assert report.summary() == ""


def test_apply_web_settings_copies_both_properties_in_one_merge():
    source = _Web(title="Source", description="The source site")
    target = _Web(title="Target", description="The target site")

    report = apply_web_settings(source, target)

    assert target.written == {"Title": "Source", "Description": "The source site"}
    assert target.updates == 1
    assert sorted(report.applied) == ["Description", "Title"]


def test_verify_web_settings_is_clean_after_a_copy():
    source = _Web(title="Source", description=None)
    target = _Web(title="Target", description="")

    apply_web_settings(source, target)

    assert verify_web_settings(source, target) == []


def test_a_failing_copy_degrades_to_a_warning():
    source = _Web(title="Source")
    target = _Web(title="Target")
    target.fail_update = True
    warnings: list[str] = []

    report = _apply_web_settings(source, target, True, warnings)

    assert report is None
    assert len(warnings) == 1
    assert warnings[0].startswith("site settings copy failed for https://contoso.sharepoint.com/sites/t")


def test_the_resolver_helper_reports_what_it_wrote():
    warnings: list[str] = []

    report = _apply_web_settings(_Web(title="Source"), _Web(title="Target"), True, warnings)

    assert report is not None
    assert warnings == ["site settings: copied Title onto https://contoso.sharepoint.com/sites/t"]
