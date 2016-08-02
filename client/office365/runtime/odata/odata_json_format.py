from abc import ABCMeta, abstractmethod


class ODataJsonFormat(object):
    """OData JSON format"""

    def __init__(self, metadata=None):
        self.metadata = metadata
        self.payload_root_entry = None
        self.payload_root_entry_collection = None

    __metaclass__ = ABCMeta

    @abstractmethod
    def build_http_headers(self):
        pass
