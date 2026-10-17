from __future__ import annotations

from enum import Enum


class ContentCategory(Enum):
    """The category of an external item (``microsoft.graph.externalConnectors.contentCategory``)."""

    uncategorized = "0"
    knowledgeBase = "1"
    wikis = "2"
    fileRepository = "3"
    qna = "4"
    crm = "5"
    dashboard = "6"
    people = "7"
    media = "8"
    email = "9"
    messaging = "10"
    meetingTranscripts = "11"
    taskManagement = "12"
    learningManagement = "13"
    unknownFutureValue = "14"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.ContentCategory"
