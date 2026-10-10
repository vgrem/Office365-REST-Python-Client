from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.principal.users.user import User


class CheckedOutFile(Entity):
    """Represents a checked-out file in a document library or workspace."""

    def takeover_checkout(self) -> Self:
        """Instructs the site that another user account is taking over control of a currently checked-out file."""
        qry = ServiceOperationQuery(self, "TakeOverCheckOut")
        self.context.add_query(qry)
        return self

    @property
    def checked_out_by_id(self) -> Optional[int]:
        """Returns the user ID of the account used to check out the file."""
        return self.properties.get("CheckedOutById", None)

    @odata(name="CheckedOutBy")
    @property
    def checked_out_by(self) -> User:
        """Returns the username of the account used to check out the file."""
        return self.properties.get(
            "CheckedOutBy",
            User(self.context, ResourcePath("CheckedOutBy", self.resource_path)),
        )

    @property
    def property_ref_name(self) -> str:
        return "CheckedOutById"

    @property
    def server_relative_path(self) -> ResourcePath:
        """Gets the ServerRelativePath property"""
        from office365.sharepoint.types.resource_path import ResourcePath

        return self.properties.get("ServerRelativePath", ResourcePath())

    def take_over_check_out(self) -> Self:
        """TakeOverCheckOut operation."""
        qry = ServiceOperationQuery(self, "TakeOverCheckOut", None, {}, None, None)
        self.context.add_query(qry)
        return self
