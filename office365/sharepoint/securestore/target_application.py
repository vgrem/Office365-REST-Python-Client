from __future__ import annotations

from typing import Optional

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.entity import Entity


class TargetApplication(Entity):
    """A logical entity that represents a software system for which credentials are maintained.
    It consists of metadata including the number and type of credentials that are required by the software system and
    a set of claims (2) that identify the administrators who can update, read, and delete the entity.
    """

    @staticmethod
    def create(context: ClientContext, application_id: str, friendly_name: str) -> "TargetApplication":
        """Creates a target application

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            application_id (str):
            friendly_name (str):
        """
        return_type = TargetApplication(context)
        payload = {"applicationId": application_id, "friendlyName": friendly_name}
        qry = ServiceOperationQuery(return_type, "", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

    @property
    def application_id(self) -> Optional[str]:
        """"""
        return self.properties.get("ApplicationId", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.SecureStoreService.Server.TargetApplication"

    @property
    def contact_email(self) -> Optional[str]:
        """Gets the ContactEmail property"""
        return self.properties.get("ContactEmail", None)

    @property
    def friendly_name(self) -> Optional[str]:
        """Gets the FriendlyName property"""
        return self.properties.get("FriendlyName", None)

    @property
    def target_app_type(self) -> Optional[int]:
        """Gets the TargetAppType property"""
        return self.properties.get("TargetAppType", None)
