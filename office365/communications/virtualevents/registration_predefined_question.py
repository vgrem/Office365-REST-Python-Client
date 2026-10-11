from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.communications.virtualevents.registrationpredefinedquestionlabel import (
        VirtualEventRegistrationPredefinedQuestionLabel,
    )


class VirtualEventRegistrationPredefinedQuestion(Entity):
    @property
    def label(self) -> VirtualEventRegistrationPredefinedQuestionLabel:
        """Gets the label property"""
        from office365.communications.virtualevents.registrationpredefinedquestionlabel import (
            VirtualEventRegistrationPredefinedQuestionLabel,
        )

        return self.properties.get("label", VirtualEventRegistrationPredefinedQuestionLabel.street)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventRegistrationPredefinedQuestion"
