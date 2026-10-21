from __future__ import annotations

from office365.runtime.odata.dialect import V3_VERBOSE
from office365.runtime.odata.json_format import JsonProfile
from office365.runtime.odata.v3.metadata_level import ODataV3MetadataLevel


class JsonLightFormat(JsonProfile):
    """JSON Light format for SharePoint Online/One Drive for Business

    The spelling of the payload is the metadata level's dialect (see
    :mod:`office365.runtime.odata.dialect`); nothing about it is decided here.
    """

    _default_dialect = V3_VERBOSE

    def __init__(self, metadata_level: ODataV3MetadataLevel = ODataV3MetadataLevel.Verbose):
        super().__init__(metadata_level)
