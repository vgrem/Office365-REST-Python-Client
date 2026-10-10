from __future__ import annotations

from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.tenant.administration.groups.info import GroupInfo


class SPOGroup(Entity):
    """ """

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = StaticPath("Microsoft.Online.SharePoint.TenantAdministration.SPOGroup")
        super().__init__(context, resource_path)

    def add_as_group_owner_and_member(self, group_id: str, user_id: str, user_principal_name: str) -> Self:
        """ """
        payload = {
            "groupId": group_id,
            "userId": user_id,
            "userPrincipalName": user_principal_name,
        }
        qry = ServiceOperationQuery(self, "AddAsGroupOwnerAndMember", None, payload, None)
        self.context.add_query(qry)
        return self

    def get_group_info(self, group_id):
        """"""
        return_type = ClientResult(self.context, GroupInfo())
        payload = {"groupId": group_id}
        qry = ServiceOperationQuery(self, "GetGroupInfo", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOGroup"

    def add_group_member(self, group_id: UUID, member_id: UUID, member_principal_name: str) -> Self:
        """AddGroupMember operation.

        Args:
            group_id (UUID):
                groupId parameter
            member_id (UUID):
                memberId parameter
            member_principal_name (str):
                memberPrincipalName parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddGroupMember",
            None,
            {"groupId": group_id, "memberId": member_id, "memberPrincipalName": member_principal_name},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_group_owner(self, group_id: UUID, owner_id: UUID, owner_principal_name: str) -> Self:
        """AddGroupOwner operation.

        Args:
            group_id (UUID):
                groupId parameter
            owner_id (UUID):
                ownerId parameter
            owner_principal_name (str):
                ownerPrincipalName parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddGroupOwner",
            None,
            {"groupId": group_id, "ownerId": owner_id, "ownerPrincipalName": owner_principal_name},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def remove_as_group_owner_and_member(self, group_id: UUID, user_id: UUID) -> Self:
        """RemoveAsGroupOwnerAndMember operation.

        Args:
            group_id (UUID):
                groupId parameter
            user_id (UUID):
                userId parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveAsGroupOwnerAndMember", None, {"groupId": group_id, "userId": user_id}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_group_member(self, group_id: UUID, member_id: UUID) -> Self:
        """RemoveGroupMember operation.

        Args:
            group_id (UUID):
                groupId parameter
            member_id (UUID):
                memberId parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveGroupMember", None, {"groupId": group_id, "memberId": member_id}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_group_owner(self, group_id: UUID, owner_id: UUID) -> Self:
        """RemoveGroupOwner operation.

        Args:
            group_id (UUID):
                groupId parameter
            owner_id (UUID):
                ownerId parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveGroupOwner", None, {"groupId": group_id, "ownerId": owner_id}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_group_properties(self, group_id: UUID, display_name: str) -> Self:
        """UpdateGroupProperties operation.

        Args:
            group_id (UUID):
                groupId parameter
            display_name (str):
                displayName parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateGroupProperties", None, {"groupId": group_id, "displayName": display_name}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_group_properties_by_site_id(self, group_id: UUID, site_id: UUID, display_name: str) -> Self:
        """UpdateGroupPropertiesBySiteId operation.

        Args:
            group_id (UUID):
                groupId parameter
            site_id (UUID):
                siteId parameter
            display_name (str):
                displayName parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateGroupPropertiesBySiteId",
            None,
            {"groupId": group_id, "siteId": site_id, "displayName": display_name},
            None,
            None,
        )
        self.context.add_query(qry)
        return self
