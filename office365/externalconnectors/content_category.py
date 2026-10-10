from __future__ import annotations

from enum import Enum


class ContentCategory(Enum):
    none = "0"
    ai = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ContentCategory"

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
