from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.communications.virtualevents.registrationquestionanswerinputtype import (
        VirtualEventRegistrationQuestionAnswerInputType,
    )


class VirtualEventRegistrationCustomQuestion(Entity):
    @property
    def answer_choices(self) -> StringCollection:
        """Gets the answerChoices property"""
        return self.properties.get("answerChoices", StringCollection())

    @property
    def answer_input_type(self) -> VirtualEventRegistrationQuestionAnswerInputType:
        """Gets the answerInputType property"""
        from office365.communications.virtualevents.registrationquestionanswerinputtype import (
            VirtualEventRegistrationQuestionAnswerInputType,
        )

        return self.properties.get("answerInputType", VirtualEventRegistrationQuestionAnswerInputType.text)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventRegistrationCustomQuestion"
