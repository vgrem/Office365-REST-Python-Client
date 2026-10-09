from datetime import datetime
from typing import Optional, Union

from typing_extensions import Self

from office365.runtime.converters.scalars import iso_z
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class Subscription(Entity):
    """A subscription for receiving notifications at a specified endpoint."""

    @property
    def id(self) -> Optional[str]:
        """Gets the unique identifier of the subscription."""
        return self.properties.get("id", None)

    @property
    def application_id(self) -> Optional[str]:
        """Identifier of the application used to create the subscription."""
        return self.properties.get("applicationId", None)

    @property
    def notification_url(self) -> Optional[str]:
        """Gets endpoint that will be called when an event occurs."""
        return self.properties.get("notificationUrl", None)

    @notification_url.setter
    def notification_url(self, value: str) -> None:
        """Sets endpoint that will be called when an event occurs."""
        self.set_property("notificationUrl", value)

    @property
    def expiration_datetime(self) -> Optional[datetime]:
        """Gets endpoint that will be called when an event occurs."""
        return self.properties.get("expirationDateTime", None)

    @expiration_datetime.setter
    def expiration_datetime(self, value: Union[datetime, str]) -> None:
        """Sets endpoint that will be called when an event occurs."""
        if isinstance(value, datetime):
            self.set_property("expirationDateTime", iso_z(value))
        else:
            self.set_property("expirationDateTime", value)

    def set_property(self, name, value, persist_changes=True):
        if self._resource_path is None:
            if name == "id":
                assert self._parent_collection is not None
                self._resource_path = ServiceOperationPath("getById", [value], self._parent_collection.resource_path)
        return super().set_property(name, value, persist_changes)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Webhooks.Subscription"

    @property
    def client_state(self) -> Optional[str]:
        """Gets the clientState property"""
        return self.properties.get("clientState", None)

    @property
    def resource(self) -> Optional[str]:
        """Gets the resource property"""
        return self.properties.get("resource", None)

    @property
    def resource_data(self) -> Optional[str]:
        """Gets the resourceData property"""
        return self.properties.get("resourceData", None)

    @property
    def scenarios(self) -> StringCollection:
        """Gets the scenarios property"""
        return self.properties.get("scenarios", StringCollection())

    def delete(self) -> Self:
        """Delete operation."""
        qry = ServiceOperationQuery(self, "Delete", None, {}, None, None)
        self.context.add_query(qry)
        return self
