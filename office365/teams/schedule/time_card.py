from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.outlook.mail.item_body import ItemBody
    from office365.teams.schedule.confirmedby import ConfirmedBy
    from office365.teams.schedule.time_card_break import TimeCardBreak
    from office365.teams.schedule.time_card_entry import TimeCardEntry
    from office365.teams.schedule.time_card_event import TimeCardEvent
    from office365.teams.schedule.time_card_state import TimeCardState


class TimeCard(Entity):
    @property
    def breaks(self) -> ClientValueCollection[TimeCardBreak]:
        """Gets the breaks property"""
        from office365.teams.schedule.time_card_break import TimeCardBreak

        return self.properties.get("breaks", ClientValueCollection[TimeCardBreak](TimeCardBreak))

    @property
    def clock_in_event(self) -> TimeCardEvent:
        """Gets the clockInEvent property"""
        from office365.teams.schedule.time_card_event import TimeCardEvent

        return self.properties.get("clockInEvent", TimeCardEvent())

    @property
    def clock_out_event(self) -> TimeCardEvent:
        """Gets the clockOutEvent property"""
        from office365.teams.schedule.time_card_event import TimeCardEvent

        return self.properties.get("clockOutEvent", TimeCardEvent())

    @property
    def confirmed_by(self) -> ConfirmedBy:
        """Gets the confirmedBy property"""
        from office365.teams.schedule.confirmedby import ConfirmedBy

        return self.properties.get("confirmedBy", ConfirmedBy.none)

    @property
    def notes(self) -> ItemBody:
        """Gets the notes property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("notes", ItemBody())

    @property
    def original_entry(self) -> TimeCardEntry:
        """Gets the originalEntry property"""
        from office365.teams.schedule.time_card_entry import TimeCardEntry

        return self.properties.get("originalEntry", TimeCardEntry())

    @property
    def state(self) -> TimeCardState:
        """Gets the state property"""
        from office365.teams.schedule.time_card_state import TimeCardState

        return self.properties.get("state", TimeCardState.clockedIn)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TimeCard"
