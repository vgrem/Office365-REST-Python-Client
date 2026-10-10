from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class UserFirstRun(Entity):
    @property
    def experiences(self) -> ClientValueCollection[int]:
        """Gets the Experiences property"""
        return self.properties.get("Experiences", ClientValueCollection(int))

    @staticmethod
    def set_experience(
        context: ClientContext, experience_id: int, reset: bool
    ) -> ClientResult[ClientValueCollection[int]]:
        """SetExperience operation.

        Args:
            experience_id (int):
                experienceId parameter
            reset (bool):
                reset parameter
        """
        from office365.sharepoint.sitedesigns.userfirstrun import UserFirstRun

        return_type = ClientResult(context, ClientValueCollection(int))
        qry = ServiceOperationQuery(
            UserFirstRun(context),
            "SetExperience",
            None,
            {"experienceId": experience_id, "reset": reset},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def set_experiences(context: ClientContext, experiences: str) -> ClientResult[ClientValueCollection[int]]:
        """SetExperiences operation.

        Args:
            experiences (str):
                experiences parameter
        """
        from office365.sharepoint.sitedesigns.userfirstrun import UserFirstRun

        return_type = ClientResult(context, ClientValueCollection(int))
        qry = ServiceOperationQuery(
            UserFirstRun(context), "SetExperiences", None, {"experiences": experiences}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
