from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from office365.runtime.client_value import ClientValue


@dataclass
class ListCreationInformation(ClientValue):
    CustomSchemaXml: str | None = None
    Description: str | None = None
    DocumentTemplateType: int | None = None
    QuickLaunchOption: int | None = None
    TemplateFeatureId: UUID | None = None
    TemplateType: int | None = None
    Title: str | None = None
    Url: str | None = None
