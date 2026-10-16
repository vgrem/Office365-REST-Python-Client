"""Best-effort copy of a web's navigation (Quick Launch and top navigation bar).

The item adapters carry content; the web's navigation is handled here. Nodes are
copied **additively**: a source node that is already present on the target (by
title) is left alone and its children are reconciled, so re-running is idempotent
and a target's own links are never destroyed. Source links are rewritten from the
source web's path to the target's, so a migrated node keeps working.

Out of scope (and reported as such): nodes without a URL (the dynamic *Recent*
node and its computed children), audience targeting, title translations, and
page/web-part content. This is the *OOTB* navigation SPMT preserves, not managed
or structural navigation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from office365.sharepoint.navigation.nodes.creationinformation import (
    NavigationNodeCreationInformation,
)


@dataclass
class NavNode:
    """A navigation node: link identity plus its (recursively captured) children."""

    title: str
    url: str
    is_external: bool = False
    is_visible: bool = True
    children: list[NavNode] = field(default_factory=list)


@dataclass
class WebNavigation:
    """A web's navigation: whether it inherits, and both link bars."""

    use_shared: bool = False
    quick_launch: list[NavNode] = field(default_factory=list)
    top_navigation_bar: list[NavNode] = field(default_factory=list)


def _capture_node(node: Any) -> NavNode:
    """Capture one node; a node without a URL is a leaf (its children are computed)."""
    url = node.url or ""
    return NavNode(
        title=node.title or "",
        url=url,
        is_external=bool(node.is_external),
        is_visible=node.is_visible if node.is_visible is not None else True,
        children=[] if not url else [_capture_node(child) for child in node.children.get().execute_query()],
    )


def capture_navigation(web) -> WebNavigation:
    """Read a web's navigation (both bars, recursively)."""
    navigation = web.navigation.get().execute_query()
    return WebNavigation(
        use_shared=bool(navigation.use_shared),
        quick_launch=[_capture_node(node) for node in navigation.quick_launch.get().execute_query()],
        top_navigation_bar=[_capture_node(node) for node in navigation.top_navigation_bar.get().execute_query()],
    )


def _web_url(web) -> str:
    """A web's absolute URL — its own ``Url`` when loaded, else the context base URL."""
    value = getattr(web, "url", None)
    if value:
        return value
    return getattr(getattr(web, "context", None), "base_url", "") or ""


def _prefixes(source_web, target_web) -> tuple[str, str]:
    """The source/target web URL prefixes (absolute and server-relative) to rewrite."""
    return _web_url(source_web).rstrip("/"), _web_url(target_web).rstrip("/")


def _rewrite_url(url: str, source: str, target: str) -> str:
    """Point a source-web link at the target web (absolute or server-relative)."""
    for prefix, replacement in ((source, target), (urlparse(source).path, urlparse(target).path)):
        if prefix and url.startswith(prefix) and url[len(prefix) : len(prefix) + 1] in ("", "/"):
            return replacement.rstrip("/") + url[len(prefix) :]
    return url


def _sync_nodes(source_nodes: list[NavNode], target_collection, source: str, target: str, warnings: list[str]) -> bool:
    """Add source nodes missing from the target collection; reconcile their children."""
    by_title = {node.title: node for node in target_collection.get().execute_query()}
    added = False
    for node in source_nodes:
        if not node.url:
            warnings.append(f"navigation node {node.title!r} has no URL (dynamic) — skipped")
            continue
        if node.is_visible is False:
            warnings.append(f"navigation node {node.title!r} is hidden on the source; copied visible")
        current = by_title.get(node.title)
        if current is None:
            info = NavigationNodeCreationInformation(
                Title=node.title,
                Url=_rewrite_url(node.url, source, target),
                IsExternal=node.is_external,
                AsLastNode=True,
            )
            current = target_collection.add(info).execute_query()  # materialize to get an Id for children
            by_title[node.title] = current
            added = True
        if node.children:
            added |= _sync_nodes(node.children, current.children, source, target, warnings)
    return added


def apply_navigation(source_web, target_web, warnings: list[str]) -> None:
    """Copy the source web's Quick Launch and top navigation onto the target (additive).

    A source web that inherits its parent's navigation only flips the target's
    ``use_shared`` flag. Unresolvable/dynamic nodes and any failure are reported
    through ``warnings``; nothing is deleted.
    """
    source = capture_navigation(source_web)
    navigation = target_web.navigation.get().execute_query()
    if source.use_shared:
        if navigation.use_shared is not True:
            navigation.use_shared = True
            navigation.update()
            target_web.context.execute_query()
        return
    if navigation.use_shared is True:
        navigation.use_shared = False
        navigation.update()
        target_web.context.execute_query()

    prefixes = _prefixes(source_web, target_web)
    wrote = False
    for source_nodes, collection in (
        (source.quick_launch, navigation.quick_launch),
        (source.top_navigation_bar, navigation.top_navigation_bar),
    ):
        if source_nodes:
            wrote |= _sync_nodes(source_nodes, collection, *prefixes, warnings)
    if wrote:
        target_web.context.execute_query()


def _verify_bar(
    label: str,
    source_nodes: list[NavNode],
    target_nodes: list[NavNode],
    source: str,
    target: str,
    issues: list[str],
) -> None:
    by_title = {node.title: node for node in target_nodes}
    for node in source_nodes:
        if not node.url:
            continue
        current = by_title.get(node.title)
        expected = _rewrite_url(node.url, source, target)
        if current is None:
            issues.append(f"{label}: node {node.title!r} was not created on the target")
            continue
        if current.url != expected:
            issues.append(f"{label}: node {node.title!r} points at {current.url!r}, expected {expected!r}")
        if node.children:
            _verify_bar(f"{label} > {node.title}", node.children, current.children, source, target, issues)


def verify_navigation(source_web, target_web) -> list[str]:
    """Reconcile a migrated web's navigation against the source.

    Returns notes for links a copy did not land (empty means the copyable links
    match). Dynamic nodes without a URL are out of scope and never reported.
    """
    source = capture_navigation(source_web)
    target = capture_navigation(target_web)
    issues: list[str] = []
    if source.use_shared != target.use_shared:
        issues.append(
            f"navigation inheritance differs (source use_shared={source.use_shared}, target={target.use_shared})"
        )
    if source.use_shared:
        return issues
    prefixes = _prefixes(source_web, target_web)
    _verify_bar("quick launch", source.quick_launch, target.quick_launch, *prefixes, issues)
    _verify_bar("top navigation", source.top_navigation_bar, target.top_navigation_bar, *prefixes, issues)
    return issues


__all__ = [
    "NavNode",
    "WebNavigation",
    "apply_navigation",
    "capture_navigation",
    "verify_navigation",
]
