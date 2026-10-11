from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.mime_content import MimeContent
    from office365.intune.devices.install_state import DeviceInstallState
    from office365.intune.devices.management.managed.ebook.e_book_assignment import ManagedEBookAssignment
    from office365.intune.devices.management.managed.ebook.install_summary import (
        EBookInstallSummary,
    )
    from office365.intune.devices.management.managed.ebook.user_install_state_summary import (
        UserInstallStateSummary,
    )


class ManagedEBook(Entity):
    """An abstract class containing the base properties for Managed eBook."""

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def information_url(self) -> Optional[str]:
        """Gets the informationUrl property"""
        return self.properties.get("informationUrl", None)

    @property
    def last_modified_date_time(self) -> datetime:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def privacy_information_url(self) -> Optional[str]:
        """Gets the privacyInformationUrl property"""
        return self.properties.get("privacyInformationUrl", None)

    @property
    def published_date_time(self) -> datetime:
        """Gets the publishedDateTime property"""
        return self.properties.get("publishedDateTime", datetime.min)

    @property
    def publisher(self) -> Optional[str]:
        """Gets the publisher property"""
        return self.properties.get("publisher", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedEBook"

    @property
    def large_cover(self) -> MimeContent:
        """Gets the largeCover property"""
        from office365.common.mime_content import MimeContent

        return self.properties.get("largeCover", MimeContent())

    @property
    def assignments(self) -> EntityCollection[ManagedEBookAssignment]:
        """Gets the assignments property"""
        from office365.intune.devices.management.managed.ebook.e_book_assignment import ManagedEBookAssignment

        return self.properties.get(
            "assignments",
            EntityCollection[ManagedEBookAssignment](
                self.context, ManagedEBookAssignment, ResourcePath("assignments", self.resource_path)
            ),
        )

    @property
    def device_states(self) -> EntityCollection[DeviceInstallState]:
        """Gets the deviceStates property"""
        from office365.intune.devices.install_state import DeviceInstallState

        return self.properties.get(
            "deviceStates",
            EntityCollection[DeviceInstallState](
                self.context, DeviceInstallState, ResourcePath("deviceStates", self.resource_path)
            ),
        )

    @property
    def install_summary(self) -> EBookInstallSummary:
        """Gets the installSummary property"""
        from office365.intune.devices.management.managed.ebook.install_summary import (
            EBookInstallSummary,
        )

        return self.properties.get(
            "installSummary", EBookInstallSummary(self.context, ResourcePath("installSummary", self.resource_path))
        )

    @property
    def user_state_summary(self) -> EntityCollection[UserInstallStateSummary]:
        """Gets the userStateSummary property"""
        from office365.intune.devices.management.managed.ebook.user_install_state_summary import (
            UserInstallStateSummary,
        )

        return self.properties.get(
            "userStateSummary",
            EntityCollection[UserInstallStateSummary](
                self.context, UserInstallStateSummary, ResourcePath("userStateSummary", self.resource_path)
            ),
        )
