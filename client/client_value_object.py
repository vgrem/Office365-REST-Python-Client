class ClientValueObject(object):
    """Base client value object"""

    def __init__(self):
        self.__metadata_type = None

    @property
    def metadata_type(self):
        return self.__metadata_type

    @metadata_type.setter
    def metadata_type(self, value):
        self.__metadata_type = value

    def ensure_metadata_type(self, entity):
        """Ensures metadata type is contained in payload"""
        entity["__metadata"] = {'type': self.metadata_type}

    @property
    def metadata(self):
        """Generates resource payload for REST endpoint"""
        #entity = dict(self.__dict__)
        entity = dict((k, v) for k, v in self.__dict__.iteritems() if v)
        self.ensure_metadata_type(entity)
        del entity["_ClientValueObject__metadata_type"]
        return entity
