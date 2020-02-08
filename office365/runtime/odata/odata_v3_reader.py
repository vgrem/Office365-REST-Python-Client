import xml.etree.ElementTree as ET

from office365.runtime.odata.odata_base_reader import ODataBaseReader
from office365.runtime.odata.odata_model import ODataModel


class ODataV3Reader(ODataBaseReader):
    """OData v3 reader"""

    def __init__(self, options):
        self._options = options
        self._namespaces = {}

    def generate_model(self):
        pass
