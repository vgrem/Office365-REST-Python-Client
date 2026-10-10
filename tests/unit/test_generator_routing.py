"""Offline tests for the layered router (namespace, exact type, prefix)."""

from __future__ import annotations

from generator.routing import Router, route_namespace


def test_route_namespace_longest_prefix_wins():
    routing = {"SP": "office365.sharepoint", "SP.Directory": "office365.sharepoint.directory"}
    assert route_namespace("SP.Directory.Provider", routing) == "office365.sharepoint.directory.provider"
    assert route_namespace("SP.Web", routing) == "office365.sharepoint.web"
    assert route_namespace("Other.Thing", routing) == ""


def test_router_prefers_exact_then_namespace_then_prefix():
    router = Router(
        namespace={"microsoft.graph.security": "office365.directory.security"},
        types={"microsoft.graph.Special": "office365.special", "Edu*": "office365.education"},
    )
    assert router.module_for("microsoft.graph.Special") == "office365.special"  # exact
    assert router.module_for("microsoft.graph.security.Alert") == "office365.directory.security"  # namespace
    assert router.module_for("microsoft.graph.EduThing") == "office365.education"  # prefix
    assert router.module_for("microsoft.graph.Unknown") is None  # unrouted


def test_router_from_options():
    router = Router.from_options(
        {"routing_SP": "office365.sharepoint", "type_routing": {"microsoft.graph.KeyValue": "office365.common"}}
    )
    assert router.namespace == {"SP": "office365.sharepoint"}
    assert router.module_for("microsoft.graph.KeyValue") == "office365.common"
