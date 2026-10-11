from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onedrive.termstore.groups.group import Group
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string


class GroupCollection(EntityCollection[Group]):
    def __init__(self, context, resource_path=None):
        super().__init__(context, Group, resource_path)

    @require_permission(
        delegated=["TermStore.ReadWrite.All"],
        application=["TermStore.ReadWrite.All"],
        notes="Create a new term store group",
    )
    def add(self, display_name: str) -> Group:
        """Create a new group object in a term store.

        Args:
            display_name (str): Name of the group to be created.
        """
        props = {"displayName": display_name}
        return super().add(**props)

    @require_permission(
        delegated=["TermStore.Read.All", "TermStore.ReadWrite.All"],
        application=["TermStore.Read.All", "TermStore.ReadWrite.All"],
        notes="Get a term store group by name",
    )
    def find_by_name(self, name: str, *, required: bool = False) -> Group:
        """Look up a term store group by its ``displayName``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        group matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The group display name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> Group:
        """Deprecated alias of :meth:`find_by_name` (strict)."""
        return self.find_by_name(name, required=True)

    def ensure(self, name: str) -> Group:
        """Gets existing group by name or creates a new one (idempotent)."""
        from office365.runtime.queries.get_or_create import create_or_get

        return create_or_get(
            create=lambda: self.add(name),
            find=lambda: self.find_by_name(name, required=True),
        )
