from abc import ABCMeta, abstractmethod
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ODataJsonFormat(object):
    """OData JSON format"""

    def __init__(self, metadata=None):
        """

        :type metadata: str
        """
        self.metadata = metadata
        self.security_tag_name = None
        self.function_tag_name = None
        self.collection_tag_name = None
        self.collection_next_tag_name = None

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_media_type(self):
        pass
