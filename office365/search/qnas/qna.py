from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.intune.devices.platformtype import DevicePlatformType
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.search.answers.answer import SearchAnswer
from office365.search.answers.state import AnswerState

if TYPE_CHECKING:
    from office365.search.answers.keyword import AnswerKeyword
    from office365.search.answers.variant import AnswerVariant


class Qna(SearchAnswer):
    """Represents a question and answer (Q&A) in Microsoft Search. Q&As are administrative answer results in the
    search results page that provide answers for specific search keywords. Q&As allow administrators
    to answer the user's questions directly in search instead of providing a link to a webpage.
    A Q&A has many properties that allow administrators to make common resources more accessible in their organization.
    """

    @property
    def availability_end_date_time(self) -> Optional[datetime]:
        """Gets the availabilityEndDateTime property"""
        return self.properties.get("availabilityEndDateTime", datetime.min)

    @property
    def availability_start_date_time(self) -> Optional[datetime]:
        """Gets the availabilityStartDateTime property"""
        return self.properties.get("availabilityStartDateTime", datetime.min)

    @property
    def group_ids(self) -> StringCollection:
        """Gets the groupIds property"""
        return self.properties.get("groupIds", StringCollection(None))

    @property
    def is_suggested(self) -> Optional[bool]:
        """Gets the isSuggested property"""
        return self.properties.get("isSuggested", None)

    @property
    def language_tags(self) -> StringCollection:
        """Gets the languageTags property"""
        return self.properties.get("languageTags", StringCollection(None))

    @property
    def platforms(self) -> ClientValueCollection[DevicePlatformType]:
        """Gets the platforms property"""
        return self.properties.get("platforms", ClientValueCollection[DevicePlatformType](DevicePlatformType))

    @property
    def state(self) -> AnswerState:
        """Gets the state property"""
        return self.properties.get("state", AnswerState.published)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.search.Qna"

    @property
    def keywords(self) -> AnswerKeyword:
        """Gets the keywords property"""
        from office365.search.answers.keyword import AnswerKeyword

        return self.properties.get("keywords", AnswerKeyword())

    @property
    def targeted_variations(self) -> ClientValueCollection[AnswerVariant]:
        """Gets the targetedVariations property"""
        from office365.search.answers.variant import AnswerVariant

        return self.properties.get("targetedVariations", ClientValueCollection[AnswerVariant](AnswerVariant))
