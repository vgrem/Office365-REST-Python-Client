class ClientValueObject(object):
    """Base client value object"""

    def set_property(self, k, v, persist_changes=True):
        self.__dict__[k] = v

    def get_property(self, k):
        return self.__dict__[k]

    def to_json(self):
        return dict((k, v) for k, v in vars(self).items() if v is not None)

    @property
    def entityTypeName(self):
        return None
