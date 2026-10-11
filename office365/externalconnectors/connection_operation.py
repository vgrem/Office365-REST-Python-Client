from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.externalconnectors.connectionoperationstatus import (
    ConnectionOperationStatus,
)
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.runtime.types.public_error import PublicError


class ConnectionOperation(PollableOperation, Entity):
    @property
    def status(self) -> ConnectionOperationStatus:
        """Gets the status property"""
        return self.properties.get("status", ConnectionOperationStatus.unspecified)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.ConnectionOperation"

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())
