from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat


class GraphRequest(ODataRequest):

    def __init__(self):
        super(GraphRequest, self).__init__(V4JsonFormat())
