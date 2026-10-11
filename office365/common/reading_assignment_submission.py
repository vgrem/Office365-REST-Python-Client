from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.education.challenging_word import ChallengingWord


class ReadingAssignmentSubmission(Entity):
    @property
    def accuracy_score(self) -> Optional[float]:
        """Gets the accuracyScore property"""
        return self.properties.get("accuracyScore", None)

    @property
    def action(self) -> Optional[str]:
        """Gets the action property"""
        return self.properties.get("action", None)

    @property
    def assignment_id(self) -> Optional[str]:
        """Gets the assignmentId property"""
        return self.properties.get("assignmentId", None)

    @property
    def challenging_words(self) -> ClientValueCollection[ChallengingWord]:
        """Gets the challengingWords property"""
        from office365.education.challenging_word import ChallengingWord

        return self.properties.get("challengingWords", ClientValueCollection[ChallengingWord](ChallengingWord))

    @property
    def class_id(self) -> Optional[str]:
        """Gets the classId property"""
        return self.properties.get("classId", None)

    @property
    def insertions(self) -> Optional[int]:
        """Gets the insertions property"""
        return self.properties.get("insertions", None)

    @property
    def mispronunciations(self) -> Optional[int]:
        """Gets the mispronunciations property"""
        return self.properties.get("mispronunciations", None)

    @property
    def missed_exclamation_marks(self) -> Optional[int]:
        """Gets the missedExclamationMarks property"""
        return self.properties.get("missedExclamationMarks", None)

    @property
    def missed_periods(self) -> Optional[int]:
        """Gets the missedPeriods property"""
        return self.properties.get("missedPeriods", None)

    @property
    def missed_question_marks(self) -> Optional[int]:
        """Gets the missedQuestionMarks property"""
        return self.properties.get("missedQuestionMarks", None)

    @property
    def missed_shorts(self) -> Optional[int]:
        """Gets the missedShorts property"""
        return self.properties.get("missedShorts", None)

    @property
    def monotone_score(self) -> Optional[float]:
        """Gets the monotoneScore property"""
        return self.properties.get("monotoneScore", None)

    @property
    def omissions(self) -> Optional[int]:
        """Gets the omissions property"""
        return self.properties.get("omissions", None)

    @property
    def repetitions(self) -> Optional[int]:
        """Gets the repetitions property"""
        return self.properties.get("repetitions", None)

    @property
    def self_corrections(self) -> Optional[int]:
        """Gets the selfCorrections property"""
        return self.properties.get("selfCorrections", None)

    @property
    def student_id(self) -> Optional[str]:
        """Gets the studentId property"""
        return self.properties.get("studentId", None)

    @property
    def submission_date_time(self) -> Optional[datetime]:
        """Gets the submissionDateTime property"""
        return self.properties.get("submissionDateTime", datetime.min)

    @property
    def submission_id(self) -> Optional[str]:
        """Gets the submissionId property"""
        return self.properties.get("submissionId", None)

    @property
    def unexpected_pauses(self) -> Optional[int]:
        """Gets the unexpectedPauses property"""
        return self.properties.get("unexpectedPauses", None)

    @property
    def word_count(self) -> Optional[int]:
        """Gets the wordCount property"""
        return self.properties.get("wordCount", None)

    @property
    def words_per_minute(self) -> Optional[float]:
        """Gets the wordsPerMinute property"""
        return self.properties.get("wordsPerMinute", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ReadingAssignmentSubmission"
