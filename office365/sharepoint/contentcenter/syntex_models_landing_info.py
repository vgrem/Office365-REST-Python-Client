from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SyntexModelsLandingInfo(Entity):
    """ """

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SyntexModelsLandingInfo"

    @property
    def document_understanding_model_display_name(self) -> Optional[str]:
        """Gets the DocumentUnderstandingModelDisplayName property"""
        return self.properties.get("DocumentUnderstandingModelDisplayName", None)

    @property
    def document_understanding_model_landing_url(self) -> Optional[str]:
        """Gets the DocumentUnderstandingModelLandingUrl property"""
        return self.properties.get("DocumentUnderstandingModelLandingUrl", None)

    @property
    def form_processing_model_display_name(self) -> Optional[str]:
        """Gets the FormProcessingModelDisplayName property"""
        return self.properties.get("FormProcessingModelDisplayName", None)

    @property
    def form_processing_model_landing_url(self) -> Optional[str]:
        """Gets the FormProcessingModelLandingUrl property"""
        return self.properties.get("FormProcessingModelLandingUrl", None)
