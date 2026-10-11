from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.outlook.mail.item_body import ItemBody


class DayNote(Entity):
    @property
    def day_note_date(self) -> Optional[date]:
        """Gets the dayNoteDate property"""
        return self.properties.get("dayNoteDate", None)

    @property
    def draft_day_note(self) -> ItemBody:
        """Gets the draftDayNote property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("draftDayNote", ItemBody())

    @property
    def shared_day_note(self) -> ItemBody:
        """Gets the sharedDayNote property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("sharedDayNote", ItemBody())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DayNote"
