"""Unit tests for CamlQuery introspection and the list-view-threshold guard."""

from __future__ import annotations

import pytest
from office365.sharepoint.listitems.caml.guard import (
    threshold_warnings,
    warn_if_unpaged,
)
from office365.sharepoint.listitems.caml.query import CamlQuery


def _query(xml: str) -> CamlQuery:
    query = CamlQuery()
    query.ViewXml = xml
    return query


def test_is_paged_detects_paged_row_limit():
    assert _query("<View><RowLimit Paged='TRUE'>100</RowLimit></View>").is_paged
    assert _query('<View><RowLimit Paged="TRUE">100</RowLimit></View>').is_paged
    assert not _query("<View><RowLimit>100</RowLimit></View>").is_paged


def test_threshold_warnings_name_the_columns():
    query = _query("<View><Query><OrderBy><FieldRef Name='date'/></OrderBy></Query></View>")

    (message,) = threshold_warnings(query)

    assert "'date'" in message
    assert "ensure_indexed" in message


def test_threshold_warnings_empty_for_plain_query_on_unknown_list():
    assert threshold_warnings(_query("<View><Query></Query></View>")) == []


def test_warn_if_unpaged_emits():
    query = _query("<View><Query><OrderBy><FieldRef Name='date'/></OrderBy></Query></View>")

    with pytest.warns(UserWarning, match="not paged"):
        warn_if_unpaged(query)
