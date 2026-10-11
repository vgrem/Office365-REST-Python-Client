from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.booking.customers.answerinputtype import AnswerInputType


class BookingCustomQuestion(Entity):
    """Represents a custom question for a bookingBusiness."""

    @property
    def answer_input_type(self) -> AnswerInputType:
        """Gets the answerInputType property"""
        from office365.booking.customers.answerinputtype import AnswerInputType

        return self.properties.get("answerInputType", AnswerInputType.text)

    @property
    def answer_options(self) -> StringCollection:
        """Gets the answerOptions property"""
        return self.properties.get("answerOptions", StringCollection())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_updated_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdatedDateTime property"""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BookingCustomQuestion"
