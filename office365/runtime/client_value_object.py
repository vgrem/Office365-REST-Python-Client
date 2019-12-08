class ClientValueObject(object):
    """Base client value object"""

    @property
    def typeName(self):
        return None

    @property
    def tagName(self):
        return None
