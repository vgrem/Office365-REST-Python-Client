from office365.runtime.odata.odata_json_format import ODataJsonFormat


class V4JsonFormat(ODataJsonFormat):
    """V4 JSON format"""

    def __init__(self, metadata):
        super(V4JsonFormat, self).__init__(metadata)
        """The IEEE754Compatible format parameter indicates that the service MUST serialize Edm.Int64 and
        Edm.Decimal numbers as strings."""
        self.IEEE754Compatible = False
        """"""
        self.streaming = False
        self.payload_root_entry_collection = "value"

    def build_http_headers(self):
        type_string = "application/json;odata.metadata={0};odata.streaming={1};IEEE754Compatible={2}" \
            .format(self.metadata, self.streaming, self.IEEE754Compatible)
        return {'content-type': type_string,
                'accept': type_string}
