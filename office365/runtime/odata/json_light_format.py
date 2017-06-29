from office365.runtime.odata.odata_json_format import ODataJsonFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class JsonLightFormat(ODataJsonFormat):
    """JSON Light format for SharePoint Online/One Drive for Business"""

    def __init__(self, metadata):
        super(JsonLightFormat, self).__init__(metadata)
        if self.metadata == ODataMetadataLevel.Verbose:
            self.payload_root_entry = "d"
            self.payload_root_entry_collection = "results"
        else:
            self.payload_root_entry_collection = "value"

    def build_http_headers(self):
        if self.metadata is None:
            return {}
        return {'content-type': 'application/json;odata={0}'.format(self.metadata),
                'accept': 'application/json;odata={0}'.format(self.metadata)}
