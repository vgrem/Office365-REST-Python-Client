class ClientValue(object):
    """Represent complex type.
    Complex types consist of a list of properties with no key, and can therefore only exist as properties of a
    containing entity or as a temporary value
    """

    def __init__(self):
        super(ClientValue, self).__init__()

    def set_property(self, k, v, persist_changes=True):
        if hasattr(self, k):
            prop_type = getattr(self, k)
            if isinstance(prop_type, ClientValue):
                [prop_type.set_property(k, v, persist_changes) for k, v in v.items()]
                setattr(self, k, prop_type)
            else:
                setattr(self, k, v)
        else:
            setattr(self, k, v)

    def get_property(self, k):
        return getattr(self, k)

    def to_json(self):
        return dict((k, v) for k, v in vars(self).items() if v is not None)

    @property
    def entity_type_name(self):
        return None

    @property
    def is_server_object_null(self):
        return not self.to_json()
