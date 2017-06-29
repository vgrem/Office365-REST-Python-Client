from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path import ResourcePath


class ResourcePathServiceOperation(ResourcePath):
    """ Resource path to address Service Operations which
    represents simple functions exposed by an OData service"""

    def __init__(self, context, parent, method_name, method_parameters=None):
        super(ResourcePathServiceOperation, self).__init__(context, parent)
        self._method_name = method_name
        self._method_parameters = method_parameters

    @property
    def url(self):
        return ODataPathParser.from_method(self._method_name, self._method_parameters)
