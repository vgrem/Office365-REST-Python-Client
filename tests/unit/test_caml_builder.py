"""Unit tests for the typed CAML query builder."""

from __future__ import annotations

from office365.sharepoint.listitems.caml import Caml, CamlQuery
from office365.sharepoint.views.scope import ViewScope


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
