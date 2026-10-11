from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class SpeakerAssignmentSubmission(Entity):
    @property
    def assignment_id(self) -> Optional[str]:
        """Gets the assignmentId property"""
        return self.properties.get("assignmentId", None)

    @property
    def average_words_per_minute_pace(self) -> Optional[int]:
        """Gets the averageWordsPerMinutePace property"""
        return self.properties.get("averageWordsPerMinutePace", None)

    @property
    def class_id(self) -> Optional[str]:
        """Gets the classId property"""
        return self.properties.get("classId", None)

    @property
    def filler_words_occurrences_count(self) -> Optional[int]:
        """Gets the fillerWordsOccurrencesCount property"""
        return self.properties.get("fillerWordsOccurrencesCount", None)

    @property
    def incorrect_camera_distance_occurrences_count(self) -> Optional[int]:
        """Gets the incorrectCameraDistanceOccurrencesCount property"""
        return self.properties.get("incorrectCameraDistanceOccurrencesCount", None)

    @property
    def length_of_submission_in_seconds(self) -> Optional[float]:
        """Gets the lengthOfSubmissionInSeconds property"""
        return self.properties.get("lengthOfSubmissionInSeconds", None)

    @property
    def lost_eye_contact_occurrences_count(self) -> Optional[int]:
        """Gets the lostEyeContactOccurrencesCount property"""
        return self.properties.get("lostEyeContactOccurrencesCount", None)

    @property
    def monotone_occurrences_count(self) -> Optional[int]:
        """Gets the monotoneOccurrencesCount property"""
        return self.properties.get("monotoneOccurrencesCount", None)

    @property
    def non_inclusive_language_occurrences_count(self) -> Optional[int]:
        """Gets the nonInclusiveLanguageOccurrencesCount property"""
        return self.properties.get("nonInclusiveLanguageOccurrencesCount", None)

    @property
    def obstructed_view_occurrences_count(self) -> Optional[int]:
        """Gets the obstructedViewOccurrencesCount property"""
        return self.properties.get("obstructedViewOccurrencesCount", None)

    @property
    def repetitive_language_occurrences_count(self) -> Optional[int]:
        """Gets the repetitiveLanguageOccurrencesCount property"""
        return self.properties.get("repetitiveLanguageOccurrencesCount", None)

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
    def top_filler_words(self) -> StringCollection:
        """Gets the topFillerWords property"""
        return self.properties.get("topFillerWords", StringCollection())

    @property
    def top_mispronounced_words(self) -> StringCollection:
        """Gets the topMispronouncedWords property"""
        return self.properties.get("topMispronouncedWords", StringCollection())

    @property
    def top_non_inclusive_words_and_phrases(self) -> StringCollection:
        """Gets the topNonInclusiveWordsAndPhrases property"""
        return self.properties.get("topNonInclusiveWordsAndPhrases", StringCollection())

    @property
    def top_repetitive_words_and_phrases(self) -> StringCollection:
        """Gets the topRepetitiveWordsAndPhrases property"""
        return self.properties.get("topRepetitiveWordsAndPhrases", StringCollection())

    @property
    def words_spoken_count(self) -> Optional[int]:
        """Gets the wordsSpokenCount property"""
        return self.properties.get("wordsSpokenCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SpeakerAssignmentSubmission"
