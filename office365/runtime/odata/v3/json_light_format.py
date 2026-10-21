from __future__ import annotations

from office365.runtime.odata.dialect import JsonDialect, dialect_for_level
from office365.runtime.odata.json_format import JsonProfile
from office365.runtime.odata.v3.metadata_level import ODataV3MetadataLevel


class JsonLightFormat(JsonProfile):
    """JSON Light format for SharePoint Online/One Drive for Business

    The spelling of the payload is the metadata level's dialect (see
    :mod:`office365.runtime.odata.dialect`); the level itself only decides
    whether control information is written at all.
    """

    def __init__(self, metadata_level: ODataV3MetadataLevel = ODataV3MetadataLevel.Verbose):
        super().__init__(metadata_level)

    @property
    def dialect(self) -> JsonDialect:
        return dialect_for_level(self.metadata_level)

    @property
    def media_type(self):
        assert isinstance(self.metadata_level, ODataV3MetadataLevel)
        return f"application/json;odata={self.metadata_level.value}"

    @property
    def include_control_information(self):
        return self.metadata_level in {ODataV3MetadataLevel.Verbose, ODataV3MetadataLevel.MinimalMetadata}
