from __future__ import annotations

from typing import Optional

from office365.directory.protection.threatassessment.requests.request import (
    ThreatAssessmentRequest,
)
from office365.runtime.types.odata_property import odata


class FileAssessmentRequest(ThreatAssessmentRequest):
    """Used to create and retrieve a file threat assessment, derived from threatAssessmentRequest.

    The file can be a text file or Word document or binary file received in an email attachment.
    """

    @odata(name="fileName")
    @property
    def file_name(self) -> Optional[str]:
        """The name of the file to assess."""
        return self.properties.get("fileName", None)

    @property
    def content_data(self) -> Optional[str]:
        """Gets the contentData property"""
        return self.properties.get("contentData", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FileAssessmentRequest"
