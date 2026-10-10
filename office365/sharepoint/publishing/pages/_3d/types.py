from __future__ import annotations

from office365.sharepoint.publishing.pages.fields_data import SitePageFieldsData


class SitePage3DFieldsData(SitePageFieldsData):
    SpaceContent: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "SP.Publishing.SitePage3DFieldsData"
