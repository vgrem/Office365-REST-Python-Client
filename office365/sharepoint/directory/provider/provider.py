from __future__ import annotations

from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection
from office365.sharepoint.directory.provider.object_data import DirectoryObjectData
from office365.sharepoint.entity import Entity


class SharePointDirectoryProvider(Entity):
    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = StaticPath("SP.Directory.Provider.SharePointDirectoryProvider")
        super().__init__(context, resource_path)

    def check_site_availability(self, site_url: str) -> ClientResult[bool]:
        """"""
        from office365.sharepoint.directory.helper import SPHelper

        return SPHelper.check_site_availability(self.context, site_url)

    def read_directory_object(self, data: DirectoryObjectData) -> ClientResult[DirectoryObjectData]:
        """"""
        return_type = ClientResult(self.context, DirectoryObjectData())
        payload = {"data": data}
        qry = ServiceOperationQuery(self, "ReadDirectoryObject", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Directory.Provider.SharePointDirectoryProvider"

    def create_directory_object(self, data: DirectoryObjectData) -> ClientResult[DirectoryObjectData]:
        """CreateDirectoryObject operation.

        Args:
            data (DirectoryObjectData):
                data parameter
        """
        from office365.sharepoint.directory.provider.object_data import (
            DirectoryObjectData,
        )

        return_type = ClientResult(self.context, DirectoryObjectData())
        qry = ServiceOperationQuery(self, "CreateDirectoryObject", None, {"data": data}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_directory_object(self, data: DirectoryObjectData) -> Self:
        """DeleteDirectoryObject operation.

        Args:
            data (DirectoryObjectData):
                data parameter
        """
        qry = ServiceOperationQuery(self, "DeleteDirectoryObject", None, {"data": data}, None, None)
        self.context.add_query(qry)
        return self

    def get_or_create_unified_group_tenant_instance_id(
        self, group_id: UUID, tenant_instance_id: UUID
    ) -> ClientResult[UUID]:
        """GetOrCreateUnifiedGroupTenantInstanceId operation.

        Args:
            group_id (UUID):
                groupId parameter
            tenant_instance_id (UUID):
                tenantInstanceId parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(
            self,
            "GetOrCreateUnifiedGroupTenantInstanceId",
            None,
            {"groupId": group_id, "tenantInstanceId": tenant_instance_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_or_create_unified_group_with_preferred_data_location(
        self, group_id: UUID, preferred_data_location: str
    ) -> ClientResult[UUID]:
        """GetOrCreateUnifiedGroupWithPreferredDataLocation operation.

        Args:
            group_id (UUID):
                groupId parameter
            preferred_data_location (str):
                preferredDataLocation parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(
            self,
            "GetOrCreateUnifiedGroupWithPreferredDataLocation",
            None,
            {"groupId": group_id, "preferredDataLocation": preferred_data_location},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def notify_data_changes(self, data: DirectoryObjectData) -> Self:
        """NotifyDataChanges operation.

        Args:
            data (DirectoryObjectData):
                data parameter
        """
        qry = ServiceOperationQuery(self, "NotifyDataChanges", None, {"data": data}, None, None)
        self.context.add_query(qry)
        return self

    def read_directory_object_batch(
        self, ids: list[UUID], object_type: int
    ) -> ClientResult[ClientValueCollection[DirectoryObjectData]]:
        """ReadDirectoryObjectBatch operation.

        Args:
            ids (list[UUID]):
                ids parameter
            object_type (int):
                objectType parameter
        """
        from office365.sharepoint.directory.provider.object_data import (
            DirectoryObjectData,
        )

        return_type = ClientResult(self.context, ClientValueCollection[DirectoryObjectData]())
        qry = ServiceOperationQuery(
            self,
            "ReadDirectoryObjectBatch",
            None,
            {"ids": GuidCollection(ids), "objectType": object_type},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def update_cache(self, data: DirectoryObjectData) -> Self:
        """UpdateCache operation.

        Args:
            data (DirectoryObjectData):
                data parameter
        """
        qry = ServiceOperationQuery(self, "UpdateCache", None, {"data": data}, None, None)
        self.context.add_query(qry)
        return self

    def update_directory_object(self, data: DirectoryObjectData) -> Self:
        """UpdateDirectoryObject operation.

        Args:
            data (DirectoryObjectData):
                data parameter
        """
        qry = ServiceOperationQuery(self, "UpdateDirectoryObject", None, {"data": data}, None, None)
        self.context.add_query(qry)
        return self
