from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class Windows10SecureAssessmentConfiguration(Entity):
    @property
    def allow_printing(self) -> Optional[bool]:
        """Gets the allowPrinting property"""
        return self.properties.get("allowPrinting", None)

    @property
    def allow_screen_capture(self) -> Optional[bool]:
        """Gets the allowScreenCapture property"""
        return self.properties.get("allowScreenCapture", None)

    @property
    def allow_text_suggestion(self) -> Optional[bool]:
        """Gets the allowTextSuggestion property"""
        return self.properties.get("allowTextSuggestion", None)

    @property
    def configuration_account(self) -> Optional[str]:
        """Gets the configurationAccount property"""
        return self.properties.get("configurationAccount", None)

    @property
    def launch_uri(self) -> Optional[str]:
        """Gets the launchUri property"""
        return self.properties.get("launchUri", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Windows10SecureAssessmentConfiguration"
