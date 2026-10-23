"""Tests for the identifier-to-snake_case conversion used by the generator."""

from __future__ import annotations

import pytest
from generator.builders.naming import to_snake_case


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("EmailIDs", "email_ids"),
        ("IDs", "ids"),
        ("URLs", "urls"),
        ("HTTPServer", "http_server"),
        ("ParentIDId", "parent_id_id"),
        ("AllowSelectSGsInODBList", "allow_select_sgs_in_odb_list"),
        ("AmIFollowedBy", "am_i_followed_by"),
        ("siteId", "site_id"),
        ("SharePointIds", "sharepoint_ids"),
        ("PageLoadTimeInMS", "page_load_time_in_ms"),
        ("iCalUId", "ical_uid"),
        ("iOS", "ios"),
        ("ASite", "a_site"),
        ("OData__AuthorByline", "o_data__author_byline"),
        ("Access_x0020_RequestsItem", "access_x0020_requests_item"),
    ],
)
def test_to_snake_case(name: str, expected: str):
    assert to_snake_case(name) == expected


def test_keywords_get_suffix_builtins_do_not():
    assert to_snake_case("Class") == "class_"
    assert to_snake_case("Import") == "import_"
    # builtins are valid member names and are used across the codebase
    assert to_snake_case("ID") == "id"
    assert to_snake_case("Type") == "type"
    assert to_snake_case("List") == "list"
    assert to_snake_case("ID", avoid_keywords=False) == "id"
