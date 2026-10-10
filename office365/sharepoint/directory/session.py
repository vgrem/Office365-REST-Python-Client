from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.directory.users.user import User
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.directory.groups.namevalidationresult import (
        GroupNameValidationResult,
    )


class DirectorySession(Entity):
    @property
    def resource_path(self):
        if self._resource_path is None:
            self._resource_path = StaticPath("SP.Directory.DirectorySession")
        return self._resource_path

    @property
    def me(self) -> User:
        return self.properties.get("Me", User(self.context, ResourcePath("Me", self.resource_path)))

    def get_graph_user(self, principal_name: str) -> User:
        """Args:
        principal_name (str):
        """
        return_type = User(self.context)
        qry = ServiceOperationQuery(self, "GetGraphUser", [principal_name], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sharepoint_data_for_user(self, user_id: str) -> User:
        return_type = User(self.context)
        qry = ServiceOperationQuery(self, "GetSharePointDataForUser", [user_id], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Directory.DirectorySession"

    def get_consumer_user_test(self, property_name: str, property_value: str) -> ClientResult[StringCollection]:
        """GetConsumerUserTest operation.

        Args:
            property_name (str):
                propertyName parameter
            property_value (str):
                propertyValue parameter
        """
        return_type = ClientResult(self.context, StringCollection())
        qry = FunctionQuery(self, "GetConsumerUserTest", [property_name, property_value], return_type)
        self.context.add_query(qry)
        return return_type

    def get_user_portal_url(self, mail: str) -> ClientResult[str]:
        """GetUserPortalUrl operation.

        Args:
            mail (str):
                mail parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetUserPortalUrl", [mail], return_type)
        self.context.add_query(qry)
        return return_type

    def join_group(self, group_id: UUID) -> ClientResult[int]:
        """JoinGroup operation.

        Args:
            group_id (UUID):
                groupId parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "JoinGroup", None, {"groupId": group_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def validate_group_name(self, display_name: str, alias: str) -> ClientResult[GroupNameValidationResult]:
        """ValidateGroupName operation.

        Args:
            display_name (str):
                displayName parameter
            alias (str):
                alias parameter
        """
        from office365.sharepoint.directory.groups.namevalidationresult import (
            GroupNameValidationResult,
        )

        return_type = ClientResult(self.context, GroupNameValidationResult())
        qry = FunctionQuery(self, "ValidateGroupName", [display_name, alias], return_type)
        self.context.add_query(qry)
        return return_type
