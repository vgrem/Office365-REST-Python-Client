from abc import ABCMeta, abstractmethod


class ODataJsonFormat(object):
    """OData JSON format"""

    def __init__(self, metadata_level=None):
        """

        :type metadata_level: str
        """
        self.metadata_level = metadata_level
        self.security_tag_name = None
        self.function_tag_name = None
        self.collection_tag_name = None
        self.collection_next_tag_name = None
        self.metadata_type_tag_name = None

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_media_type(self):
        pass
