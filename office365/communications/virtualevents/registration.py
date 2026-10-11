from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.virtualevents.attendeeregistrationstatus import (
        VirtualEventAttendeeRegistrationStatus,
    )
    from office365.communications.virtualevents.external_registration_information import (
        VirtualEventExternalRegistrationInformation,
    )
    from office365.communications.virtualevents.registration_question_answer import (
        VirtualEventRegistrationQuestionAnswer,
    )
    from office365.communications.virtualevents.session import VirtualEventSession


class VirtualEventRegistration(Entity):
    @property
    def cancelation_date_time(self) -> Optional[datetime]:
        """Gets the cancelationDateTime property"""
        return self.properties.get("cancelationDateTime", datetime.min)

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def external_registration_information(self) -> VirtualEventExternalRegistrationInformation:
        """Gets the externalRegistrationInformation property"""
        from office365.communications.virtualevents.external_registration_information import (
            VirtualEventExternalRegistrationInformation,
        )

        return self.properties.get("externalRegistrationInformation", VirtualEventExternalRegistrationInformation())

    @property
    def first_name(self) -> Optional[str]:
        """Gets the firstName property"""
        return self.properties.get("firstName", None)

    @property
    def last_name(self) -> Optional[str]:
        """Gets the lastName property"""
        return self.properties.get("lastName", None)

    @property
    def preferred_language(self) -> Optional[str]:
        """Gets the preferredLanguage property"""
        return self.properties.get("preferredLanguage", None)

    @property
    def preferred_timezone(self) -> Optional[str]:
        """Gets the preferredTimezone property"""
        return self.properties.get("preferredTimezone", None)

    @property
    def registration_date_time(self) -> Optional[datetime]:
        """Gets the registrationDateTime property"""
        return self.properties.get("registrationDateTime", datetime.min)

    @property
    def registration_question_answers(self) -> ClientValueCollection[VirtualEventRegistrationQuestionAnswer]:
        """Gets the registrationQuestionAnswers property"""
        from office365.communications.virtualevents.registration_question_answer import (
            VirtualEventRegistrationQuestionAnswer,
        )

        return self.properties.get(
            "registrationQuestionAnswers",
            ClientValueCollection[VirtualEventRegistrationQuestionAnswer](VirtualEventRegistrationQuestionAnswer),
        )

    @property
    def status(self) -> VirtualEventAttendeeRegistrationStatus:
        """Gets the status property"""
        from office365.communications.virtualevents.attendeeregistrationstatus import (
            VirtualEventAttendeeRegistrationStatus,
        )

        return self.properties.get("status", VirtualEventAttendeeRegistrationStatus.registered)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def sessions(self) -> EntityCollection[VirtualEventSession]:
        """Gets the sessions property"""
        from office365.communications.virtualevents.session import VirtualEventSession

        return self.properties.get(
            "sessions",
            EntityCollection[VirtualEventSession](
                self.context, VirtualEventSession, ResourcePath("sessions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventRegistration"
