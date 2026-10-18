"""Aggregate web verification: one report, one verdict, every dimension counted."""

import json

import pytest
from office365.migration.sharepoint import site_verify
from office365.migration.sharepoint.site_verify import (
    LIST_SECURITY,
    SITE_SCOPE,
    WEB_SCOPE_STRUCTURE,
    verify_site,
)
from office365.migration.sharepoint.verify import StructureReport


class _Web:
    def __init__(self, url="https://contoso.sharepoint.com/sites/team_out"):
        self.url = url
        self.context = type("_Context", (), {"base_url": "https://contoso.sharepoint.com/sites/team_out"})()


class _Context:
    def __init__(self, web):
        self.web = web


@pytest.fixture
def contexts():
    return _Context(_Web("https://contoso.sharepoint.com/sites/team_in")), _Context(_Web())


@pytest.fixture
def clean(monkeypatch):
    """Every web-level verifier returns no findings, and records its calls."""
    calls = []

    def _note(name):
        def _run(source_web, target_web):
            calls.append(name)
            return []

        return _run

    for name, func in (
        ("settings", "verify_web_settings"),
        ("branding", "verify_web_branding"),
        ("navigation", "verify_navigation"),
        ("pages", "verify_page_copy"),
        ("security", "verify_site_security"),
        ("list security", "verify_list_security"),
    ):
        monkeypatch.setattr(site_verify, func, _note(name))
    monkeypatch.setattr(site_verify, "_web_scope_findings", _note("web-scope"))
    monkeypatch.setattr(site_verify, "_site_scope_findings", _note(SITE_SCOPE))
    return calls


def test_a_clean_web_is_ok_and_complete(contexts, clean):
    report = verify_site(*contexts)

    assert report.ok
    assert report.complete
    assert report.issues == []
    assert report.url == "https://contoso.sharepoint.com/sites/team_out"
    assert report.findings == {}
    assert report.checked == ["settings", "branding", WEB_SCOPE_STRUCTURE, SITE_SCOPE]
    assert report.summary() == (
        "OK | https://contoso.sharepoint.com/sites/team_out | settings: 0, branding: 0, "
        "web-scope structure: 0, site scope: 0"
    )
    assert json.loads(json.dumps(report.to_dict()))["ok"] is True


def test_findings_make_the_web_a_mismatch_and_are_counted(contexts, clean, monkeypatch):
    monkeypatch.setattr(
        site_verify,
        "verify_web_settings",
        lambda s, t: ["site settings: Title is 'team_out', source has 'team'"],
    )
    monkeypatch.setattr(
        site_verify, "verify_page_copy", lambda s, t: ["page: Home.aspx missing", "page: About.aspx drifted"]
    )

    report = verify_site(*contexts, pages=True)

    assert not report.ok
    assert report.complete
    assert report.findings == {
        "settings": ["site settings: Title is 'team_out', source has 'team'"],
        "pages": ["page: Home.aspx missing", "page: About.aspx drifted"],
    }
    assert report.summary() == (
        "MISMATCH | https://contoso.sharepoint.com/sites/team_out | settings: 1, branding: 0, "
        "web-scope structure: 0, site scope: 0, pages: 2"
    )
    assert report.issues[0].startswith("site settings:")
    assert len(report.issues) == len(report.findings["settings"]) + len(report.findings["pages"])


def test_a_list_acl_the_target_did_not_restore_is_its_own_dimension(contexts, clean, monkeypatch):
    monkeypatch.setattr(
        site_verify,
        "verify_list_security",
        lambda s, t: ["list 'Private' inherits the web's permissions on the target; the source restricts it"],
    )

    report = verify_site(*contexts, security=True)

    assert not report.ok
    assert report.findings == {
        LIST_SECURITY: ["list 'Private' inherits the web's permissions on the target; the source restricts it"]
    }
    assert report.summary().endswith(f"{LIST_SECURITY}: 1")


def test_the_list_check_only_runs_with_security_enabled(contexts, clean):
    verify_site(*contexts)

    assert "list security" not in clean


def test_a_check_that_cannot_run_is_unverifiable_not_a_mismatch(contexts, clean, monkeypatch):
    monkeypatch.setattr(site_verify, "verify_site_security", _raise_access_denied)

    report = verify_site(*contexts, security=True)

    assert report.ok  # nothing contradicted the target
    assert not report.complete
    assert report.unverifiable == ["security: access denied"]
    assert report.summary().startswith("PARTIAL")
    assert "security" in report.summary()
    assert json.loads(json.dumps(report.to_dict()))["complete"] is False


def _raise_access_denied(source_web, target_web):
    raise RuntimeError("access denied")


def test_only_the_requested_checks_run(contexts, clean):
    report = verify_site(
        *contexts, settings=False, branding=False, web_scope_structure=False, site_scope=False, pages=True
    )

    assert clean == ["pages"]
    assert report.checked == ["pages"]


def test_nothing_requested_reports_nothing_to_check(contexts, clean):
    report = verify_site(*contexts, settings=False, branding=False, web_scope_structure=False, site_scope=False)

    assert report.ok
    assert report.summary() == "OK | https://contoso.sharepoint.com/sites/team_out | nothing to check"


def test_list_structure_is_folded_in(contexts, clean, monkeypatch):
    monkeypatch.setattr(site_verify, "verify_list_structure", lambda s, t: StructureReport(list_title=t))

    report = verify_site(*contexts, lists=[("source", "target"), ("source2", "target2")])

    assert report.ok
    assert [item.list_title for item in report.lists] == ["target", "target2"]
    assert report.summary().startswith("OK | https://contoso.sharepoint.com/sites/team_out | lists: 2 (0 with issues)")


def test_a_failing_list_report_makes_the_web_a_mismatch(contexts, clean, monkeypatch):
    monkeypatch.setattr(
        site_verify,
        "verify_list_structure",
        lambda s, t: StructureReport(list_title=t, missing_columns=["Region"]),
    )

    report = verify_site(*contexts, lists=[("source", "target")])

    assert not report.ok
    assert report.summary().startswith("OK") is False
    assert report.summary().startswith("MISMATCH")
    assert "lists: 1 (1 with issues)" in report.summary()
    assert report.issues == [
        "MISMATCH | target | columns: 1, content types: 0, views: 0, field links: 0, settings: 0, "
        "column attributes: 0, formatting: 0"
    ]


def test_an_unreadable_list_is_unverifiable_not_fatal(contexts, clean, monkeypatch):
    monkeypatch.setattr(site_verify, "verify_list_structure", _raise_access_denied)

    report = verify_site(*contexts, lists=[(type("_L", (), {"title": "Documents"})(), "target")])

    assert report.ok
    assert not report.complete
    assert report.unverifiable == ["list structure for Documents: access denied"]


def test_structure_can_be_skipped_even_with_pairs(contexts, clean, monkeypatch):
    monkeypatch.setattr(site_verify, "verify_list_structure", lambda s, t: StructureReport(list_title="never"))

    report = verify_site(*contexts, lists=[("source", "target")], structure=False)

    assert report.lists == []
    assert "lists:" not in report.summary()


def test_branding_is_its_own_dimension(contexts, clean, monkeypatch):
    monkeypatch.setattr(
        site_verify,
        "verify_web_branding",
        lambda s, t: ["branding: https://contoso.sharepoint.com/sites/team_out MasterUrl is None, source has '/x'"],
    )

    report = verify_site(*contexts)

    assert not report.ok
    assert list(report.findings) == ["branding"]
    assert report.summary().endswith("settings: 0, branding: 1, web-scope structure: 0, site scope: 0")


def test_the_url_falls_back_to_the_context_when_a_projected_read_dropped_it(contexts, clean):
    source, target = contexts
    target.web = type(
        "_Web", (), {"context": type("_Context", (), {"base_url": "https://contoso.sharepoint.com/sites/x"})}
    )()

    assert verify_site(source, target).url == "https://contoso.sharepoint.com/sites/x"


def test_web_scope_structure_findings_are_reported_as_a_note(contexts, monkeypatch):
    monkeypatch.setattr(site_verify, "verify_web_settings", lambda s, t: [])
    monkeypatch.setattr(
        site_verify, "web_scope_note", lambda missing, url=None: "web-scope structure is not replayed: …"
    )
    monkeypatch.setattr(site_verify, "compare_web_scope_structure", lambda s, t: object())

    report = verify_site(*contexts, branding=False)

    assert report.findings == {WEB_SCOPE_STRUCTURE: ["web-scope structure is not replayed: …"]}
    assert not report.ok
