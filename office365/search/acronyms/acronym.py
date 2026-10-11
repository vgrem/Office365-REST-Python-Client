from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.search.answers.answer import SearchAnswer

if TYPE_CHECKING:
    from office365.search.answers.state import AnswerState


class Acronym(SearchAnswer):
    """Represents an acronym that is an administrative answer in Microsoft Search results to define common
    acronyms in an organization."""

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "microsoft.graph.search.acronym"

    @property
    def stands_for(self) -> Optional[str]:
        """Gets the standsFor property"""
        return self.properties.get("standsFor", None)

    @property
    def state(self) -> AnswerState:
        """Gets the state property"""
        from office365.search.answers.state import AnswerState

        return self.properties.get("state", AnswerState.published)
