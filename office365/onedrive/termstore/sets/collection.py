from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onedrive.termstore.sets.name import LocalizedName
from office365.onedrive.termstore.sets.set import Set
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.deprecated import deprecated
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery

if TYPE_CHECKING:
    from office365.onedrive.termstore.groups.group import Group


class SetCollection(EntityCollection[Set]):
    def __init__(self, context, resource_path=None, parent_group=None):
        """Args:
        parent_group (office365.onedrive.termstore.groups.group.Group): The parent group that contains the set
        """
        super().__init__(context, Set, resource_path)
        self._parent_group = parent_group

    @require_permission(
        delegated=["TermStore.Read.All", "TermStore.ReadWrite.All"],
        application=["TermStore.Read.All", "TermStore.ReadWrite.All"],
        notes="Get term set by name",
    )
    def find_by_name(self, name: str, *, required: bool = False) -> Set:
        """Look up a term set by its localized ``displayName``.

        Term sets expose their name through ``localizedNames`` rather than a
        filterable property, so the collection is fetched and matched
        client-side. Deferred — run with ``execute_query()``. Tolerant by
        default: when no set matches, the returned object is left uninitialized
        (check :attr:`~office365.runtime.client_object.ClientObject.is_loaded`).
        Pass ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The term set name (in en-US localization)
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_predicate(
            lambda s: s.display_name == name,
            f"displayName eq '{name}'",
            required=required,
        )

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> Set:
        """Deprecated alias of :meth:`find_by_name` (tolerant).

        Args:
            name (str): The term set name (in en-US localization)
        """
        return self.find_by_name(name)

    @require_permission(
        delegated=["TermStore.ReadWrite.All"],
        application=["TermStore.ReadWrite.All"],
        notes="Create a new term set",
    )
    def add(self, name: str, parent_group: Group | None = None) -> Set:
        """Create a new set object.

        Args:
            parent_group (office365.onedrive.termstore.group.Group): The parent group that contains the set.
            name (str): Default name (in en-US localization).
        """
        return_type = Set(self.context, EntityPath(None, self.resource_path))
        self.add_child(return_type)

        if self._parent_group is not None:
            props = {"localizedNames": ClientValueCollection(LocalizedName, [LocalizedName(name)])}
            qry = CreateEntityQuery(self, props, return_type)
            self.context.add_query(qry)
        elif parent_group is not None:
            props = {
                "parentGroup": {"id": parent_group.get_property("id")},
                "localizedNames": ClientValueCollection(LocalizedName, [LocalizedName(name)]),
            }
            qry = CreateEntityQuery(self, props, return_type)
            self.context.add_query(qry)
        else:
            raise TypeError("Parameter 'parent_group' is not set")

        return return_type

    def ensure_set(self, name: str) -> Set:
        """Gets existing set by name or creates a new one (idempotent)."""
        from office365.runtime.queries.get_or_create import create_or_get

        return create_or_get(create=lambda: self.add(name), find=lambda: self.find_by_name(name))
