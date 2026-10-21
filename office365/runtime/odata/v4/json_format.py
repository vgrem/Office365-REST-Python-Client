from __future__ import annotations

from office365.runtime.odata.dialect import V4_NO_METADATA
from office365.runtime.odata.json_format import JsonProfile
from office365.runtime.odata.v4.metadata_level import ODataV4MetadataLevel


class V4JsonFormat(JsonProfile):
    """JSON format (V4)"""

    _default_dialect = V4_NO_METADATA

    def __init__(self, metadata_level: str = ODataV4MetadataLevel.Minimal):
        super().__init__(metadata_level)
        """The IEEE754Compatible format parameter indicates that the service MUST serialize Edm.Int64 and
        Edm.Decimal numbers as strings."""
        self.IEEE754Compatible = False
        self.streaming = False

    @property
    def _media_type_options(self) -> str:
        return f";odata.streaming={self.streaming};IEEE754Compatible={self.IEEE754Compatible}"
