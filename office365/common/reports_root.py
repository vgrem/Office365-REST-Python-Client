from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.reading_assignment_submission import (
        ReadingAssignmentSubmission,
    )
    from office365.common.reading_coach_passage import ReadingCoachPassage
    from office365.common.reflect_check_in_response import ReflectCheckInResponse
    from office365.common.speaker_assignment_submission import (
        SpeakerAssignmentSubmission,
    )


class ReportsRoot(Entity):
    @property
    def reading_assignment_submissions(self) -> EntityCollection[ReadingAssignmentSubmission]:
        """Gets the readingAssignmentSubmissions property"""
        from office365.common.reading_assignment_submission import (
            ReadingAssignmentSubmission,
        )

        return self.properties.get(
            "readingAssignmentSubmissions",
            EntityCollection[ReadingAssignmentSubmission](
                self.context,
                ReadingAssignmentSubmission,
                ResourcePath("readingAssignmentSubmissions", self.resource_path),
            ),
        )

    @property
    def reading_coach_passages(self) -> EntityCollection[ReadingCoachPassage]:
        """Gets the readingCoachPassages property"""
        from office365.common.reading_coach_passage import ReadingCoachPassage

        return self.properties.get(
            "readingCoachPassages",
            EntityCollection[ReadingCoachPassage](
                self.context, ReadingCoachPassage, ResourcePath("readingCoachPassages", self.resource_path)
            ),
        )

    @property
    def reflect_check_in_responses(self) -> EntityCollection[ReflectCheckInResponse]:
        """Gets the reflectCheckInResponses property"""
        from office365.common.reflect_check_in_response import ReflectCheckInResponse

        return self.properties.get(
            "reflectCheckInResponses",
            EntityCollection[ReflectCheckInResponse](
                self.context, ReflectCheckInResponse, ResourcePath("reflectCheckInResponses", self.resource_path)
            ),
        )

    @property
    def speaker_assignment_submissions(self) -> EntityCollection[SpeakerAssignmentSubmission]:
        """Gets the speakerAssignmentSubmissions property"""
        from office365.common.speaker_assignment_submission import (
            SpeakerAssignmentSubmission,
        )

        return self.properties.get(
            "speakerAssignmentSubmissions",
            EntityCollection[SpeakerAssignmentSubmission](
                self.context,
                SpeakerAssignmentSubmission,
                ResourcePath("speakerAssignmentSubmissions", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ReportsRoot"
