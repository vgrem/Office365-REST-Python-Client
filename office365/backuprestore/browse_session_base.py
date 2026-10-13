from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery

if TYPE_CHECKING:
    from office365.backuprestore.restoresessions.browsable_resource_type import (
        BrowsableResourceType,
    )
    from office365.backuprestore.restoresessions.browse_query_order import BrowseQueryOrder
    from office365.backuprestore.restoresessions.browse_query_response_item import (
        BrowseQueryResponseItem,
    )
    from office365.backuprestore.restoresessions.browse_session_status import (
        BrowseSessionStatus,
    )
    from office365.runtime.client_value_collection import ClientValueCollection
    from office365.runtime.types.public_error import PublicError


class BrowseSessionBase(Entity):
    def browse(
        self,
        browse_location_item_key: str,
        browse_resource_type: BrowsableResourceType,
        filter_expression: Optional[str] = None,
        order_by: Optional[BrowseQueryOrder] = None,
    ) -> ClientResult[ClientValueCollection[BrowseQueryResponseItem]]:
        """Browse the contents of a protected location (site, library, folder).

        Args:
            browse_location_item_key: The key of the item to browse (returned by a
                previous call or the restore point).
            browse_resource_type: The kind of item that ``browse_location_item_key`` points at.
            filter_expression: Optional server-side filter applied to the results.
            order_by: Optional ordering of the returned items.
        """
        from office365.backuprestore.restoresessions.browse_query_response_item import (
            BrowseQueryResponseItem,
        )
        from office365.runtime.client_value_collection import ClientValueCollection

        return_type = ClientResult(self.context, ClientValueCollection(BrowseQueryResponseItem))
        payload = {
            "browseLocationItemKey": browse_location_item_key,
            "browseResourceType": browse_resource_type.name,
            "filter": filter_expression,
            "orderBy": order_by.name if order_by is not None else None,
        }
        qry = ServiceOperationQuery(self, "browse", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def backup_size_in_bytes(self) -> Optional[str]:
        """Gets the backupSizeInBytes property"""
        return self.properties.get("backupSizeInBytes", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def restore_point_date_time(self) -> Optional[datetime]:
        """Gets the restorePointDateTime property"""
        return self.properties.get("restorePointDateTime", datetime.min)

    @property
    def restore_point_id(self) -> Optional[str]:
        """Gets the restorePointId property"""
        return self.properties.get("restorePointId", None)

    @property
    def status(self) -> BrowseSessionStatus:
        """Gets the status property"""
        from office365.backuprestore.restoresessions.browse_session_status import (
            BrowseSessionStatus,
        )

        return self.properties.get("status", BrowseSessionStatus.creating)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BrowseSessionBase"
