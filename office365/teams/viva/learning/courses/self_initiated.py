from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.teams.viva.learning.courses.activity import LearningCourseActivity


class LearningSelfInitiatedCourse(LearningCourseActivity):
    """Represents the details of a learning course activity that is self-initiated by a user."""

    @property
    def started_date_time(self) -> Optional[datetime]:
        """Gets the startedDateTime property"""
        return self.properties.get("startedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LearningSelfInitiatedCourse"
