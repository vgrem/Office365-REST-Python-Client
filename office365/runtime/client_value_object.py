class ClientValueObject(object):
    """Base client value object"""

    def map_json(self, json):
        for key, val in json.items():
            # if hasattr(type(self), key):
            self.__dict__[key] = val

    @property
    def typeName(self):
        return None

    @property
    def tagName(self):
        return None
