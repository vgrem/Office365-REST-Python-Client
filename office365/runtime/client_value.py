class ClientValue(object):
    """Represent complex type.
    Complex types consist of a list of properties with no key, and can therefore only exist as properties of a
    containing entity or as a temporary value
    """

    def __init__(self):
        super(ClientValue, self).__init__()

    def set_property(self, k, v, persist_changes=True):
        prop_type = getattr(self, k, None)
        if isinstance(prop_type, ClientValue) and v is not None:
            if isinstance(v, list):
                [prop_type.set_property(i, p_v, persist_changes) for i, p_v in enumerate(v)]
            else:
                [prop_type.set_property(k, p_v, persist_changes) for k, p_v in v.items()]
            setattr(self, k, prop_type)
        else:
            setattr(self, k, v)

    def get_property(self, k):
        return getattr(self, k)

    def to_json(self):
        return dict((k, v) for k, v in vars(self).items() if v is not None)

    @property
    def entity_type_name(self):
        return type(self).__name__

    @property
    def is_server_object_null(self):
        return not self.to_json()
