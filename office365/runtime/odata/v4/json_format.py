from office365.runtime.odata.dialect import V4, JsonDialect
from office365.runtime.odata.json_format import JsonProfile
from office365.runtime.odata.v4.metadata_level import ODataV4MetadataLevel


class V4JsonFormat(JsonProfile):
    """JSON format (V4)"""

    def __init__(self, metadata_level: str = ODataV4MetadataLevel.Minimal):
        super().__init__(metadata_level)
        """The IEEE754Compatible format parameter indicates that the service MUST serialize Edm.Int64 and
        Edm.Decimal numbers as strings."""
        self.IEEE754Compatible = False
        self.streaming = False

    @property
    def dialect(self) -> JsonDialect:
        return V4

    @property
    def media_type(self) -> str:
        return (
            f"application/json;odata.metadata={self.metadata_level};"
            f"odata.streaming={self.streaming};"
            f"IEEE754Compatible={self.IEEE754Compatible}"
        )

    @property
    def include_control_information(self) -> bool:
        return self.metadata_level in {ODataV4MetadataLevel.Minimal, ODataV4MetadataLevel.Full}
