from __future__ import annotations

from datetime import datetime
from typing import Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.publishing.publicationmetadata import PublicationMetadata
from office365.sharepoint.publishing.sharepointids import SharePointIds


class Campaign(Entity):
    @property
    def color(self) -> Optional[str]:
        """Gets the color property"""
        return self.properties.get("color", None)

    @property
    def creation_date(self) -> datetime:
        """Gets the creationDate property"""
        return self.properties.get("creationDate", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def id(self) -> Optional[int]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def logo(self) -> Optional[str]:
        """Gets the logo property"""
        return self.properties.get("logo", None)

    @property
    def share_point_ids(self) -> SharePointIds:
        """Gets the sharePointIds property"""
        return self.properties.get("sharePointIds", SharePointIds())

    @property
    def status(self) -> Optional[str]:
        """Gets the status property"""
        return self.properties.get("status", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Publishing.Campaigns.Campaign"

    def associate(self, publication_id: int) -> Self:
        """Associate operation.

        Args:
            publication_id (int): publicationId parameter
        """
        qry = ServiceOperationQuery(self, "Associate", None, {"publicationId": publication_id}, None, None)
        self.context.add_query(qry)
        return self

    def delete(self) -> Self:
        """Delete operation."""
        qry = ServiceOperationQuery(self, "Delete", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def publications(self, offset: int, limit: int) -> ClientResult[ClientValueCollection[PublicationMetadata]]:
        """Publications operation.

        Args:
            offset (int): offset parameter
            limit (int): limit parameter
        """
        return_type = ClientResult(self.context, ClientValueCollection[PublicationMetadata]())
        qry = FunctionQuery(self, "Publications", [offset, limit], return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def sharepoint_ids(self) -> SharePointIds:
        """Gets the sharePointIds property"""
        from office365.sharepoint.publishing.sharepointids import SharePointIds

        return self.properties.get("sharePointIds", SharePointIds())
