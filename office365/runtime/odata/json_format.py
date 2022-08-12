from abc import ABCMeta


class ODataJsonFormat(object):
    """OData JSON format"""

    def __init__(self, metadata_level=None):
        """
        :type metadata_level: str
        """
        self.metadata_level = metadata_level

    __metaclass__ = ABCMeta

    @property
    def metadata_type(self):
        raise NotImplementedError

    @property
    def collection(self):
        raise NotImplementedError

    @property
    def collection_next(self):
        raise NotImplementedError

    @property
    def media_type(self):
        """
        Gets media type

        :rtype: str
        """
        raise NotImplementedError

    @property
    def include_control_information(self):
        """Determines whether control information that is represented as annotations should be included in payload

        :rtype: bool
        """
        raise NotImplementedError
