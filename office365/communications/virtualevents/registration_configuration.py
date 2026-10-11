from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.virtualevents.registration_question_base import (
        VirtualEventRegistrationQuestionBase,
    )


class VirtualEventRegistrationConfiguration(Entity):
    @property
    def capacity(self) -> Optional[int]:
        """Gets the capacity property"""
        return self.properties.get("capacity", None)

    @property
    def is_manual_approval_enabled(self) -> Optional[bool]:
        """Gets the isManualApprovalEnabled property"""
        return self.properties.get("isManualApprovalEnabled", None)

    @property
    def is_waitlist_enabled(self) -> Optional[bool]:
        """Gets the isWaitlistEnabled property"""
        return self.properties.get("isWaitlistEnabled", None)

    @property
    def registration_web_url(self) -> Optional[str]:
        """Gets the registrationWebUrl property"""
        return self.properties.get("registrationWebUrl", None)

    @property
    def questions(self) -> EntityCollection[VirtualEventRegistrationQuestionBase]:
        """Gets the questions property"""
        from office365.communications.virtualevents.registration_question_base import (
            VirtualEventRegistrationQuestionBase,
        )

        return self.properties.get(
            "questions",
            EntityCollection[VirtualEventRegistrationQuestionBase](
                self.context, VirtualEventRegistrationQuestionBase, ResourcePath("questions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventRegistrationConfiguration"
