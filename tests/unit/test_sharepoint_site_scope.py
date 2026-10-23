"""Site scope: what the target site cannot do because a migration never replays features."""

from office365.migration.sharepoint.site_scope import (
    compare_site_scope,
    site_scope_note,
)
from office365.migration.sharepoint.site_verify import SITE_SCOPE, verify_site

WEB_A = "65a86d9e-d9e0-493d-b877-f09550efdee1"
WEB_B = "b6917cb1-93a0-4b97-a84d-7cf49975d4ec"
SITE_A = "d28fa327-96ef-445e-8019-d62455a5630d"


class _Feature:
    def __init__(self, definition_id):
        self.definition_id = definition_id


class _Features:
    """An activated-feature collection: ``get()`` then ``execute_query()``."""

    def __init__(self, ids):
        self.ids = ids

    def get(self):
        return self

    def execute_query(self):
        return [_Feature(definition_id) for definition_id in self.ids]


class _TimeZone:
    def __init__(self, properties=None, error=None):
        self.properties = properties or {}
        self.error = error

    def get(self):
        return self

    def execute_query(self):
        if self.error is not None:
            raise self.error
        return self


class _RegionalSettings:
    def __init__(self, properties, zone):
        self.properties = properties
        self._zone = zone

    def get(self):
        return self

    def execute_query(self):
        return self

    @property
    def time_zone(self):
        return self._zone


class _Web:
    def __init__(self, url, web_features=(), site_features=(), regional=None, zone=None):
        self.url = url
        self.features = _Features(list(web_features))
        self.regional_settings = _RegionalSettings(regional or {}, zone or _TimeZone())


class _Site:
    def __init__(self, site_features=()):
        self.features = _Features(list(site_features))


class _Context:
    def __init__(self, url="https://contoso.sharepoint.com/sites/team_in", **kwargs):
        self.web = _Web(url, **kwargs)
        self.site = _Site(kwargs.get("site_features", ()))


PACIFIC_ID = 13
PACIFIC = {"Id": PACIFIC_ID, "Description": "(UTC-08:00) Pacific Time (US and Canada)"}
UTC = {"Id": 2, "Description": "(UTC+00:00) Dublin, Edinburgh, Lisbon, London"}


def _regional(**overrides):
    values = {
        "LocaleId": 1033,
        "WorkDays": 62,
        "FirstDayOfWeek": 0,
        "FirstWeekOfYear": 0,
        "CalendarType": 0,
        "AdjustHijriDays": 0,
        "DateSeparator": "/",
        "TimeSeparator": ":",
        "Time24": True,
        "DateFormat": 0,
    }
    values.update(overrides)
    return values


def _source(**kwargs):
    kwargs.setdefault("web_features", [WEB_A])
    kwargs.setdefault("site_features", [SITE_A])
    kwargs.setdefault("regional", _regional())
    kwargs.setdefault("zone", _TimeZone(PACIFIC))
    return _Context(**kwargs)


def _target(**kwargs):
    kwargs.setdefault("web_features", [WEB_A])
    kwargs.setdefault("site_features", [SITE_A])
    kwargs.setdefault("regional", _regional())
    kwargs.setdefault("zone", _TimeZone(PACIFIC))
    return _Context(url="https://contoso.sharepoint.com/sites/team_out", **kwargs)


def test_a_regional_difference_is_named_by_value():
    diff = compare_site_scope(
        _source(regional=_regional(LocaleId=1031), zone=_TimeZone(PACIFIC)),
        _target(regional=_regional(), zone=_TimeZone(UTC)),
    )

    assert set(diff.regional) == {"LocaleId", "TimeZoneId", "TimeZone"}
    note = site_scope_note(diff) or ""

    assert "regional settings differ" in note
    assert "Pacific Time" in note
    assert "1031 vs 1033" in note


def test_verify_site_reports_a_missing_feature_end_to_end():
    report = verify_site(
        _source(web_features=[WEB_A, WEB_B]),
        _target(web_features=[WEB_A]),
        settings=False,
        branding=False,
        web_scope_structure=False,
    )

    assert report.findings[SITE_SCOPE][0].startswith("site scope is not replayed")
    assert WEB_B in report.findings[SITE_SCOPE][0]
    assert report.summary().endswith(f"{SITE_SCOPE}: 1")
