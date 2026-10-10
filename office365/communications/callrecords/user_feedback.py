from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.callrecords.feedback_token_set import FeedbackTokenSet
from office365.communications.callrecords.user_feedback_rating import UserFeedbackRating
from office365.runtime.client_value import ClientValue


@dataclass
class UserFeedback(ClientValue):
    rating: UserFeedbackRating = UserFeedbackRating.notRated
    text: str | None = None
    tokens: FeedbackTokenSet = field(default_factory=FeedbackTokenSet)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.UserFeedback"
