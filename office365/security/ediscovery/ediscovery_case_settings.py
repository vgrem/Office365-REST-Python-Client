from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.security.cases.reviewsetsettings import ReviewSetSettings
from office365.security.cases.type import CaseType

if TYPE_CHECKING:
    from office365.security.ocr_settings import OcrSettings
    from office365.security.redundancy_detection_settings import (
        RedundancyDetectionSettings,
    )
    from office365.security.topic_modeling_settings import (
        TopicModelingSettings,
    )


class EdiscoveryCaseSettings(Entity):
    @property
    def case_type(self) -> CaseType:
        """Gets the caseType property"""
        return self.properties.get("caseType", CaseType.standard)

    @property
    def review_set_settings(self) -> ReviewSetSettings:
        """Gets the reviewSetSettings property"""
        return self.properties.get("reviewSetSettings", ReviewSetSettings.none)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryCaseSettings"

    @property
    def ocr(self) -> OcrSettings:
        """Gets the ocr property"""
        from office365.security.ocr_settings import OcrSettings

        return self.properties.get("ocr", OcrSettings())

    @property
    def redundancy_detection(self) -> RedundancyDetectionSettings:
        """Gets the redundancyDetection property"""
        from office365.security.redundancy_detection_settings import (
            RedundancyDetectionSettings,
        )

        return self.properties.get("redundancyDetection", RedundancyDetectionSettings())

    @property
    def topic_modeling(self) -> TopicModelingSettings:
        """Gets the topicModeling property"""
        from office365.security.topic_modeling_settings import (
            TopicModelingSettings,
        )

        return self.properties.get("topicModeling", TopicModelingSettings())
