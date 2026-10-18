"""Site scope: what the target site cannot do because a migration never replays features."""

import json

from office365.migration.sharepoint import site_verify
from office365.migration.sharepoint.site_scope import (
    SiteScopeDiff,
    capture_site_scope,
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


def test_an_identical_site_has_nothing_to_report():
    diff = compare_site_scope(_source(), _target())

    assert diff.is_empty
    assert diff.to_dict() == {
        "missing_web_features": [],
        "missing_site_features": [],
        "extra_web_features": [],
        "extra_site_features": [],
        "regional": {},
    }
    assert site_scope_note(diff) is None


def test_a_missing_web_feature_is_named():
    diff = compare_site_scope(_source(web_features=[WEB_A, WEB_B]), _target(web_features=[WEB_A]))

    assert diff.missing_web_features == [WEB_B]
    note = site_scope_note(diff, "https://contoso.sharepoint.com/sites/team_in")

    assert note is not None
    assert "1 web feature(s)" in note
    assert WEB_B in note
    assert "https://contoso.sharepoint.com/sites/team_in" in note
    assert "Enable-SPFeature" in note


def test_a_missing_site_collection_feature_is_named_separately():
    diff = compare_site_scope(_source(site_features=[SITE_A]), _target(site_features=[]))

    assert diff.missing_web_features == []
    assert diff.missing_site_features == [SITE_A]
    assert "site-collection feature(s)" in (site_scope_note(diff) or "")


def test_an_extra_feature_on_the_target_is_carried_but_is_not_a_finding():
    diff = compare_site_scope(_source(web_features=[WEB_A]), _target(web_features=[WEB_A, WEB_B]))

    assert diff.is_empty
    assert diff.extra_web_features == [WEB_B]
    assert diff.to_dict()["extra_web_features"] == [WEB_B]
    assert site_scope_note(diff) is None


def test_feature_ids_compare_case_and_brace_insensitively():
    diff = compare_site_scope(
        _source(web_features=["{65A86D9E-D9E0-493D-B877-F09550EFDEE1}"]),
        _target(web_features=["65a86d9e-d9e0-493d-b877-f09550efdee1"]),
    )

    assert diff.is_empty


def test_a_feature_without_an_id_is_ignored():
    diff = compare_site_scope(_source(web_features=[WEB_A, None, ""]), _target(web_features=[WEB_A]))

    assert diff.is_empty


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


def test_a_time_zone_that_cannot_be_read_is_not_a_finding():
    diff = compare_site_scope(
        _source(zone=_TimeZone(error=RuntimeError("time zone is not readable"))),
        _target(zone=_TimeZone(error=RuntimeError("time zone is not readable"))),
    )

    assert diff.is_empty
    assert site_scope_note(diff) is None


def test_a_property_the_server_does_not_return_compares_equal():
    regional = _regional()
    regional.pop("Time24")
    diff = compare_site_scope(_source(regional=dict(regional)), _target(regional=dict(regional)))

    assert diff.is_empty


def test_a_long_list_of_missing_features_is_truncated():
    missing = [f"0000000{i}-0000-0000-0000-000000000000" for i in range(7)]
    diff = SiteScopeDiff(missing_web_features=missing)

    note = site_scope_note(diff) or ""

    assert "7 web feature(s)" in note
    assert missing[4] in note
    assert missing[5] not in note
    assert "(+2 more)" in note


def test_capture_reads_web_and_site_collection_scope():
    scope = capture_site_scope(_source(web_features=[WEB_B], site_features=[SITE_A]))

    assert scope.to_dict()["web_features"] == [WEB_B]
    assert scope.to_dict()["site_features"] == [SITE_A]
    assert scope.to_dict()["regional"]["TimeZoneId"] == PACIFIC_ID
    assert scope.to_dict()["regional"]["TimeZone"] == PACIFIC["Description"]


def test_the_diff_is_json_serializable():
    diff = compare_site_scope(_source(web_features=[WEB_A, WEB_B]), _target(web_features=[]))

    payload = json.loads(json.dumps(diff.to_dict()))

    assert payload["missing_web_features"] == [WEB_A, WEB_B]


def test_verify_site_runs_the_site_scope_check_by_default(monkeypatch):
    monkeypatch.setattr(site_verify, "_site_scope_findings", lambda source, target: ["site scope is not replayed"])

    report = verify_site(_source(), _target(), settings=False, branding=False, web_scope_structure=False)

    assert report.checked == [SITE_SCOPE]
    assert report.findings == {SITE_SCOPE: ["site scope is not replayed"]}
    assert not report.ok


def test_verify_site_can_skip_the_site_scope_check():
    report = verify_site(
        _source(web_features=[WEB_A, WEB_B]),
        _target(web_features=[]),
        settings=False,
        branding=False,
        web_scope_structure=False,
        site_scope=False,
    )

    assert report.checked == []
    assert report.ok
    assert report.summary().endswith("nothing to check")


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
