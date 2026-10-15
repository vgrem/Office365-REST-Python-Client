from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from office365.onedrive.termstore.groups.collection import GroupCollection
from office365.onedrive.termstore.sets.collection import SetCollection
from office365.onedrive.termstore.terms.collection import TermCollection
from office365.runtime.client_result import ClientResult

if TYPE_CHECKING:
    from office365.onedrive.termstore.store import Store


class StoreManager:
    """Traverse, search, and import the term store hierarchy.

    All operations are deferred: queries are queued and run with a single
    ``execute_query()``. ``get_all_terms()`` returns a flattened ``TermCollection``
    with each term's ``children`` attached, so the standard collection pipeline
    (``write_csv``, or the wire ``to_json()`` payload serializer) can serialize
    the full tree.

    ``export_tree()`` / ``import_tree()`` handle the *hierarchy* (a nested
    group -> set -> term tree) and deliberately avoid the ``to_json`` /
    ``from_json`` names, which are reserved for wire-payload (de)serialization.
    """

    def __init__(self, store: Store):
        self.store = store

    def get_all_terms(self) -> TermCollection:
        """Flatten the whole term store into a single ``TermCollection``.

        Traverses groups -> sets -> terms -> children and collects every term
        into one flat collection. No queries run until ``execute_query()``.
        """
        all_terms = TermCollection(self.store.context)

        def _on_terms_loaded(terms: TermCollection) -> None:
            for term in terms:
                all_terms.add_child(term)
                term.children.get().after_execute(_on_terms_loaded)

        def _on_sets_loaded(sets: SetCollection) -> None:
            for term_set in sets:
                term_set.children.get().after_execute(_on_terms_loaded)

        def _on_groups_loaded(groups: GroupCollection) -> None:
            for group in groups:
                group.sets.get().after_execute(_on_sets_loaded)

        self.store.groups.get().after_execute(_on_groups_loaded)
        return all_terms

    def search_term(self, search_label: str) -> TermCollection:
        """Search for a term by label across all sets in the term store."""
        return_type = TermCollection(self.store.context)

        def _on_terms_loaded(terms: TermCollection) -> None:
            for t in terms:
                if t.display_name == search_label:
                    return_type.add_child(t)

        def _on_sets_loaded(sets: SetCollection) -> None:
            for s in sets:
                s.terms.get().after_execute(_on_terms_loaded)

        def _on_groups_loaded(groups: GroupCollection) -> None:
            for g in groups:
                g.sets.get().after_execute(_on_sets_loaded)

        self.store.groups.get().after_execute(_on_groups_loaded)
        return return_type

    def import_tree(self, data: list[dict]) -> Store:
        """Import a term hierarchy (a nested tree) from a list of group dicts.

        Args:
            data: List of ``{name, sets: [{name, children: [{name, children: []}]}]}``.

        Returns:
            self.store for chaining — call ``execute_query()`` to process.
        """
        for group_data in data:
            group = self.store.ensure_group(group_data["name"])
            for set_data in group_data.get("sets", []):
                term_set = group.ensure_set(set_data["name"])
                self._create_terms(term_set.children, set_data.get("children", []))
        return self.store

    def export_tree(self) -> ClientResult[list]:
        """Export the term hierarchy as a nested tree of dicts.

        Builds ``[{name, sets: [{name, children: [{name, children: []}]}]}]`` —
        the symmetric counterpart of :meth:`import_tree`. Deferred, like every
        other operation here: ``execute_query()`` then read ``result.value``.

            >>> result = store_manager.export_tree().execute_query()
            >>> tree = result.value
        """
        return_type = ClientResult(self.store.context, [])
        tree: list = []

        def _on_terms_loaded(terms: TermCollection, container: list) -> None:
            for term in terms:
                node = {"name": term.display_name, "children": []}
                container.append(node)
                term.children.get().after_execute(
                    lambda children, parent=node: _on_terms_loaded(children, parent["children"])
                )

        def _on_sets_loaded(sets: SetCollection, set_container: list) -> None:
            for term_set in sets:
                set_node = {"name": term_set.display_name, "children": []}
                set_container.append(set_node)
                term_set.children.get().after_execute(
                    lambda terms, parent=set_node: _on_terms_loaded(terms, parent["children"])
                )

        def _on_groups_loaded(groups: GroupCollection) -> None:
            for group in groups:
                group_node = {"name": group.display_name, "sets": []}
                tree.append(group_node)
                group.sets.get().after_execute(lambda sets, parent=group_node: _on_sets_loaded(sets, parent["sets"]))

        self.store.groups.get().after_execute(_on_groups_loaded)
        return_type.set_property("__value", tree)
        return return_type

    def from_json(self, data: list[dict]) -> Store:
        """Deprecated alias of :meth:`import_tree`.

        ``from_json`` is reserved for wire-payload deserialization; use
        :meth:`import_tree` for the term-store hierarchy.
        """
        warnings.warn(
            "StoreManager.from_json() is deprecated; use import_tree() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.import_tree(data)

    def to_json(self) -> ClientResult[list]:
        """Deprecated alias of :meth:`export_tree`.

        ``to_json`` is reserved for wire-payload serialization; use
        :meth:`export_tree` for the term-store hierarchy.
        """
        warnings.warn(
            "StoreManager.to_json() is deprecated; use export_tree() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.export_tree()

    def _create_terms(self, collection: TermCollection, terms: list[dict]) -> None:
        for term_data in terms:
            node = collection.ensure(term_data["name"])
            self._create_terms(node.children, term_data.get("children", []))
