from __future__ import annotations

from office365.count_collection import CountCollection
from office365.directory.groups.group import Group
from office365.directory.groups.profile import GroupProfile
from office365.directory.permissions.require_permission import require_permission
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.types.collections import StringCollection


class GroupCollection(CountCollection[Group]):
    """Group's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, Group, resource_path)

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def add(self, group_properties: GroupProfile) -> Group:
        """Create a Group resource.
        You can create the following types of groups:
        - Microsoft 365 group (unified group)
        - Security group

        Args:
            group_properties (GroupProfile): Group properties
        """
        return_type = Group(self.context)
        self.add_child(return_type)
        qry = CreateEntityQuery(self, group_properties, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def create_m365(
        self,
        name: str,
        description: str | None = None,
        owners: list[str] | None = None,
        members: list[str] | None = None,
    ) -> Group:
        """Creates a Microsoft 365 group.
        If the owners have not been specified, the calling user is automatically added as the owner of the group.

        Args:
            name (str): The display name for the group
            description (str): An optional description for the group
            owners (list[str]): The group owners
            members (list[str]): The group members
        """
        params = GroupProfile(
            mailNickname=name,
            displayName=name,
            description=description,
            mailEnabled=True,
            securityEnabled=False,
            groupTypes=StringCollection(["Unified"]),
            owners=owners,
            members=members,
        )
        return self.add(params)

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def create_security(self, name: str, description: str | None = None) -> Group:
        """Creates a Security group

        Args:
            name (str): The display name for the group
            description (str): An optional description for the group
        """
        params = GroupProfile(
            mailNickname=name,
            displayName=name,
            description=description,
            mailEnabled=False,
            securityEnabled=True,
            groupTypes=StringCollection(),
        )
        return self.add(params)

    @require_permission(
        delegated=["Group.ReadWrite.All", "Team.Create"], application=["Group.ReadWrite.All", "Team.Create"]
    )
    def create_with_team(self, group_name: str) -> Group:
        """Provision a new group along with a team.

        Note: After the group is successfully created, which can take up to 15 minutes,
        create a Microsoft Teams team using this method could throw an error since
        the group creation process might not be completed. For that scenario prefer submit the request to server via
        execute_query_retry instead of execute_query when using this method.

        Args:
            group_name (str): The display name for the group
        """

        def _after_group_created(return_type: Group) -> None:
            return_type.add_team()

        return self.create_m365(group_name).after_execute(_after_group_created)

    def find_by_name(self, name: str, *, required: bool = False) -> Group:
        """Look up a group by its ``displayName``.

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
