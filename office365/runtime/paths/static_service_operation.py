from office365.runtime.client_path import ClientPath
from office365.runtime.odata.odata_path_builder import ODataPathBuilder


class StaticServiceOperationPath(ClientPath):
    """ Resource path to address static Service Operations"""

    def __init__(self, entity, name, parameters=None):
        """
        :type name: str
        :type parameters: list or dict or office365.runtime.client_value.ClientValue or None
        """
        super(StaticServiceOperationPath, self).__init__()
        self._entity = entity
        self._name = name
        self._parameters = parameters

    @property
    def segments(self):
        return [self.delimiter, self._entity, ".", ODataPathBuilder.from_operation(self._name, self._parameters)]
