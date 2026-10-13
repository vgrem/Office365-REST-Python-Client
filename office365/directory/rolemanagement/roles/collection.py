from __future__ import annotations

from typing_extensions import Self

from office365.delta_collection import DeltaCollection
from office365.directory.rolemanagement.roles.role import DirectoryRole
from office365.directory.rolemanagement.templates.collection import DirectoryRoleTemplateCollection
from office365.directory.rolemanagement.templates.template import DirectoryRoleTemplate
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.query_capabilities import query_capabilities


@query_capabilities(
    unsupported={"top"},
    doc="https://learn.microsoft.com/en-us/graph/api/directoryrole-list",
    note="directoryRoles cannot be paged with $top",
)
class DirectoryRoleCollection(DeltaCollection[DirectoryRole]):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, DirectoryRole, resource_path)

    def find_by_name(self, name: str, *, required: bool = False) -> DirectoryRole:
        """Look up a directory role by its display name.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        role matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The display name (e.g. 'Security Administrator')
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> DirectoryRole:
        """Deprecated alias of :meth:`find_by_name` (strict).

        Args:
            name (str): The display name (e.g. 'Security Administrator')
        Returns:
            The matching DirectoryRole
        Raises:
            NotFoundException: If no role matches
            ValueError: If multiple roles match
        """
        return self.find_by_name(name, required=True)

    def assign(self, role_name: str) -> Self:
        """Activate a directory role by display name.

        Idempotent — if already activated, the server returns 409 Conflict.
        The caller can catch and ignore it.

        Args:
            role_name (str): The display name (e.g. 'Security Administrator')
        """

        def _assign(templates: DirectoryRoleTemplateCollection) -> None:
            template: DirectoryRoleTemplate | None = next((t for t in templates if t.display_name == role_name), None)
            assert template is not None and template.id is not None
            self.add(roleTemplateId=template.id)

        self.context.directory_role_templates.get().after_execute(_assign)
        return self

    def revoke(self, role_name: str) -> Self:
        """Deactivate a directory role by removing all members.

        Directory roles are system-defined and cannot be deleted.
        This removes all members, effectively deactivating the role.

        Args:
            role_name (str): The display name (e.g. 'Security Administrator')
        """

        def _get_members(role: DirectoryRole) -> None:
            def _remove_members(members):
                for member in members:
                    role.members.remove(member)

            role.members.get().after_execute(_remove_members)

        self.find_by_name(role_name, required=True).after_execute(_get_members)
        return self
