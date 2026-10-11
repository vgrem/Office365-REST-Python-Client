from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.communications.virtualevents.presenter_details import (
        VirtualEventPresenterDetails,
    )
    from office365.directory.permissions.identity import Identity


class VirtualEventPresenter(Entity):
    """Represents information about a presenter of a virtual event."""

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def identity(self) -> Identity:
        """Gets the identity property"""
        from office365.directory.permissions.identity import Identity

        return self.properties.get("identity", Identity())

    @property
    def presenter_details(self) -> VirtualEventPresenterDetails:
        """Gets the presenterDetails property"""
        from office365.communications.virtualevents.presenter_details import (
            VirtualEventPresenterDetails,
        )

        return self.properties.get("presenterDetails", VirtualEventPresenterDetails())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventPresenter"
