"""Aggregate web verification: one report, one verdict, every dimension counted."""

import json

import pytest
from office365.migration.sharepoint import site_verify
from office365.migration.sharepoint.site_verify import (
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
