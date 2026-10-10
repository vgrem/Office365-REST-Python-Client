from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class ClientWebPart(Entity):
    """Representation of a ClientWebPart. It provides with ClientWebPart metadata and methods to render it."""

    def render(self, properties=None):
        """Renders the ClientWebPart.  Returns HTML that can be inserted in a page.

        Args:
            properties (dict): Properties for the ClientWebPart, including edit mode.
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Render", None, properties, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)
