from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.applications.assignmenttype import AssignmentType
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
    from office365.outlook.mail.item_body import ItemBody


class LearningAssignment(Entity):
    @property
    def assigned_date_time(self) -> Optional[datetime]:
        """Gets the assignedDateTime property"""
        return self.properties.get("assignedDateTime", datetime.min)

    @property
    def assigner_user_id(self) -> Optional[str]:
        """Gets the assignerUserId property"""
        return self.properties.get("assignerUserId", None)

    @property
    def assignment_type(self) -> AssignmentType:
        """Gets the assignmentType property"""
        from office365.directory.applications.assignmenttype import AssignmentType

        return self.properties.get("assignmentType", AssignmentType.required)

    @property
    def due_date_time(self) -> DateTimeTimeZone:
        """Gets the dueDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("dueDateTime", DateTimeTimeZone())

    @property
    def notes(self) -> ItemBody:
        """Gets the notes property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("notes", ItemBody())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LearningAssignment"
