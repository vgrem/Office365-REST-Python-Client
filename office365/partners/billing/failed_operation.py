from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.runtime.types.public_error import PublicError


class FailedOperation(PollableOperation, Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.partners.billing.FailedOperation"

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())
