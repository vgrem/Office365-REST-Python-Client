from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v3.json_light_format import JsonLightFormat


class SharePointRequest(ODataRequest):

    def __init__(self):
        super().__init__(JsonLightFormat())
