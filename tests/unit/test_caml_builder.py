"""Unit tests for the typed CAML query builder."""

from __future__ import annotations

from datetime import datetime

import pytest
from office365.sharepoint.listitems.caml import Caml, CamlQuery, FieldRef
from office365.sharepoint.views.scope import ViewScope


def test_eq_renders_comparison():
    xml = Caml.eq("Status", "Active").to_xml()

    assert xml == '<Eq><FieldRef Name="Status"/><Value Type="Text">Active</Value></Eq>'


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        ("x", "Text"),
        (5, "Integer"),
        (5.5, "Number"),
        (True, "Boolean"),
        (datetime(2024, 1, 2, 3, 4), "DateTime"),
    ],
)
def test_value_type_inference(value, expected_type):
    assert f'Type="{expected_type}"' in Caml.eq("F", value).to_xml()


def test_text_is_xml_escaped():
    assert "A &amp; B &lt;c&gt;" in Caml.eq("Title", "A & B <c>").to_xml()


def test_fluent_or_chain_is_binary_nested():
    expr = (
        Caml.text("Email")
        .eq("a")
        .or_(Caml.text("Email").eq("b"))
        .or_(Caml.text("Title").begins_with("[G]"))
        .or_(Caml.text("Content").contains("G"))
    )
    xml = expr.to_xml()

    assert xml.count("<Or>") == 3  # noqa: PLR2004 — 4 conditions -> 3 nested Or
    assert xml.count("<Or>") == xml.count("</Or>")
    # never a 3-child <Or>
    assert "<Or><Or>" in xml


def test_variadic_and_folds_left():
    xml = Caml.and_(Caml.eq("A", 1), Caml.eq("B", 2), Caml.eq("C", 3)).to_xml()

    assert xml.count("<And>") == 2  # noqa: PLR2004
    assert xml == (
        '<And><And><Eq><FieldRef Name="A"/><Value Type="Integer">1</Value></Eq>'
        '<Eq><FieldRef Name="B"/><Value Type="Integer">2</Value></Eq></And>'
        '<Eq><FieldRef Name="C"/><Value Type="Integer">3</Value></Eq></And>'
    )


def test_operators_match_methods():
    a, b = Caml.eq("A", 1), Caml.eq("B", 2)

    assert (a & b).to_xml() == a.and_(b).to_xml()
    assert (a | b).to_xml() == a.or_(b).to_xml()
    assert (~a).to_xml() == "<Not>" + a.to_xml() + "</Not>"


def test_lookup_id_in_renders_integer_values():
    xml = Caml.lookup("Category").id().in_([2, 3, 10]).to_xml()

    assert '<FieldRef Name="Category" LookupId="TRUE"/>' in xml
    assert xml.count('Type="Integer"') == 3  # noqa: PLR2004
    assert "<Values>" in xml


def test_now_value_node():
    xml = Caml.date("ExpirationDate").leq(Caml.now).to_xml()

    assert '<Value Type="DateTime"><Now/></Value>' in xml


def test_is_null_and_not():
    assert Caml.is_null("Title").to_xml() == '<IsNull><FieldRef Name="Title"/></IsNull>'
    assert Caml.is_not_null("Title").to_xml() == '<IsNotNull><FieldRef Name="Title"/></IsNotNull>'


def test_membership_and_date_ranges_overlap():
    assert "CurrentUserGroups" in Caml.membership("AssignedTo").to_xml()
    assert "<DateRangesOverlap>" in Caml.date_ranges_overlap("EventDate", Caml.today).to_xml()


def test_builder_renders_full_view():
    query = (
        CamlQuery.builder()
        .where(Caml.text("Status").eq("Active"))
        .order_by("Created", ascending=False)
        .group_by("Category")
        .row_limit(2000)
        .scope(ViewScope.RecursiveAll)
        .view_fields("ID", "Title")
        .build()
    )

    assert query.ViewXml is not None
    assert query.ViewXml.startswith('<View Scope="RecursiveAll">')
    assert '<ViewFields><FieldRef Name="ID"/><FieldRef Name="Title"/></ViewFields>' in query.ViewXml
    assert '<GroupBy><FieldRef Name="Category" Collapse="TRUE"/></GroupBy>' in query.ViewXml
    assert '<OrderBy><FieldRef Name="Created" Ascending="FALSE"/></OrderBy>' in query.ViewXml
    assert '<RowLimit Paged="TRUE">2000</RowLimit>' in query.ViewXml
    assert query.is_paged


def test_builder_field_refs_exclude_view_fields():
    query = CamlQuery.builder().where(Caml.eq("Status", "Active")).order_by("Created").view_fields("ID", "Title").build()

    assert query.field_refs == {"Status", "Created"}


def test_field_ref_ascending():
    ref = FieldRef("Created").desc()
    assert ref.to_xml() == '<FieldRef Name="Created" Ascending="FALSE"/>'


def test_expression_bool_raises():
    with pytest.raises(TypeError, match="cannot be used with Python"):
        bool(Caml.eq("A", 1))


def test_to_json_excludes_the_ast():
    query = CamlQuery.builder().where(Caml.eq("A", 1)).build()

    payload = query.to_json()

    assert "ViewXml" in payload
    assert all(not key.startswith("_") for key in payload)
    assert not any("expr" in key for key in payload)


def test_parse_still_works_without_ast():
    query = CamlQuery.parse("<OrderBy><FieldRef Name='Created'/></OrderBy>")

    assert query.field_refs == {"Created"}  # regex fallback
    assert query.is_paged is False
