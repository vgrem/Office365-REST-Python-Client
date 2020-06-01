class ClientValueObject(object):
    """Base client value object"""

    def __init__(self):
        super(ClientValueObject, self).__init__()

    def set_property(self, k, v, persist_changes=True):
        self.__dict__[k] = v

    def get_property(self, k):
        return self.__dict__[k]

    def to_json(self):
        return dict((k, v) for k, v in vars(self).items() if v is not None)

    @property
    def entity_type_name(self):
        return None

    @property
    def is_server_object_null(self):
        return not self.to_json()
