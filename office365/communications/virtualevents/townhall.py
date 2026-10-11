from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.communications.virtualevents.virtual_event import VirtualEvent
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.meetings.audience import MeetingAudience
    from office365.communications.user_identity import CommunicationsUserIdentity
    from office365.communications.virtualevents.registration import (
        VirtualEventRegistration,
    )
    from office365.communications.virtualevents.townhall_registration_configuration import (
        VirtualEventTownhallRegistrationConfiguration,
    )
    from office365.directory.permissions.identity import Identity


class VirtualEventTownhall(VirtualEvent):
    """Represents information about a virtual event town hall."""

    @property
    def audience(self) -> MeetingAudience:
        """Gets the audience property"""
        from office365.communications.meetings.audience import MeetingAudience

        return self.properties.get("audience", MeetingAudience.everyone)

    @property
    def capacity(self) -> Optional[int]:
        """Gets the capacity property"""
        return self.properties.get("capacity", None)

    @property
    def co_organizers(self) -> ClientValueCollection[CommunicationsUserIdentity]:
        """Gets the coOrganizers property"""
        from office365.communications.user_identity import CommunicationsUserIdentity

        return self.properties.get(
            "coOrganizers", ClientValueCollection[CommunicationsUserIdentity](CommunicationsUserIdentity)
        )

    @property
    def invited_attendees(self) -> ClientValueCollection[Identity]:
        """Gets the invitedAttendees property"""
        from office365.directory.permissions.identity import Identity

        return self.properties.get("invitedAttendees", ClientValueCollection[Identity](Identity))

    @property
    def is_invite_only(self) -> Optional[bool]:
        """Gets the isInviteOnly property"""
        return self.properties.get("isInviteOnly", None)

    @property
    def registration_configuration(self) -> VirtualEventTownhallRegistrationConfiguration:
        """Gets the registrationConfiguration property"""
        from office365.communications.virtualevents.townhall_registration_configuration import (
            VirtualEventTownhallRegistrationConfiguration,
        )

        return self.properties.get(
            "registrationConfiguration",
            VirtualEventTownhallRegistrationConfiguration(
                self.context, ResourcePath("registrationConfiguration", self.resource_path)
            ),
        )

    @property
    def registrations(self) -> EntityCollection[VirtualEventRegistration]:
        """Gets the registrations property"""
        from office365.communications.virtualevents.registration import (
            VirtualEventRegistration,
        )

        return self.properties.get(
            "registrations",
            EntityCollection[VirtualEventRegistration](
                self.context, VirtualEventRegistration, ResourcePath("registrations", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventTownhall"
