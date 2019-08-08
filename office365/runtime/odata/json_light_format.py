from office365.runtime.odata.odata_json_format import ODataJsonFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class JsonLightFormat(ODataJsonFormat):
    """JSON Light format for SharePoint Online/One Drive for Business"""

    def __init__(self, metadata):
        super(JsonLightFormat, self).__init__(metadata)
        if self.metadata == ODataMetadataLevel.Verbose:
            self.security_tag_name = "d"
            self.collection_tag_name = "results"
            self.collection_next_tag_name = "__next"
        else:
            self.collection_next_tag_name = "value"

    def build_http_headers(self):
        if self.metadata is None:
            return {}
        return {'content-type': 'application/json;odata={0}'.format(self.metadata),
                'accept': 'application/json;odata={0}'.format(self.metadata)}
