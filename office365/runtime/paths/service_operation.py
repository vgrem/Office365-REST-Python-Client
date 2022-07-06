from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.odata.path_builder import ODataPathBuilder


class ServiceOperationPath(ResourcePath):
    """Path to address Service Operations which represents simple functions exposed by an OData service"""

    def __init__(self, name, parameters=None, parent=None):
        """
        :type parameters: list or dict or office365.runtime.client_value.ClientValue or None
        :type name: str
        :type parent: office365.runtime.paths.resource_path.ResourcePath
        """
        super(ServiceOperationPath, self).__init__(name, parent)
        self._parameters = parameters

    @property
    def segments(self):
        return [self.delimiter, ODataPathBuilder.build(self._name, self._parameters)]
