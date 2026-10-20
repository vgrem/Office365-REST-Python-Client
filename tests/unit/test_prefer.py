"""Unit tests for the ``Prefer`` request-header helpers."""

from __future__ import annotations

from office365.runtime.http.prefer import (
    CREATE_IF_MISSING,
    RETURN_REPRESENTATION,
    add_prefer,
    prefer_create_if_missing,
    prefer_outlook_timezone,
    prefer_return_representation,
    prefer_upsert,
)
from office365.runtime.http.request_options import RequestOptions


def _request(headers: dict | None = None) -> RequestOptions:
    return RequestOptions(url="https://graph.microsoft.com/v1.0/groups", headers=headers or {})


def test_prefer_upsert_sets_both_values() -> None:
    request = _request()

    prefer_upsert(request)

    assert request.headers["Prefer"] == f"{CREATE_IF_MISSING}, {RETURN_REPRESENTATION}"


def test_prefer_upsert_is_idempotent_and_merges() -> None:
    request = _request({"Prefer": "include-unknown-enum-members"})

    prefer_upsert(request)
    prefer_upsert(request)

    assert request.headers["Prefer"] == (f"include-unknown-enum-members, {CREATE_IF_MISSING}, {RETURN_REPRESENTATION}")


def test_prefer_create_if_missing_and_representation_compose() -> None:
    request = _request()

    prefer_create_if_missing(request)
    prefer_return_representation(request)

    assert request.headers["Prefer"] == f"{CREATE_IF_MISSING}, {RETURN_REPRESENTATION}"


def test_add_prefer_does_not_duplicate_an_existing_value() -> None:
    request = _request({"Prefer": CREATE_IF_MISSING})

    add_prefer(request, CREATE_IF_MISSING, RETURN_REPRESENTATION)

    assert request.headers["Prefer"] == f"{CREATE_IF_MISSING}, {RETURN_REPRESENTATION}"


def test_prefer_outlook_timezone_quotes_the_zone_and_merges() -> None:
    request = _request({"Prefer": "return=representation"})

    prefer_outlook_timezone(request, "W. Europe Standard Time")

    assert request.headers["Prefer"] == 'return=representation, outlook.timezone="W. Europe Standard Time"'
